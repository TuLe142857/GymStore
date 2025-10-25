import click
import json
import os
from flask.cli import with_appcontext
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Product, Category, Brand, Ingredient, ProductIngredient


import os
import requests

SERVER_IMAGE_STORAGE_DIR = "uploads/product_images"
SERVER_IMAGE_UPLOAD_URL = "http://localhost:5000/api/uploads/product_images"

def download_img(url: str, path: str) -> bool:
    try:

        os.makedirs(os.path.dirname(path), exist_ok=True)

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()


        with open(path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return True

    except Exception as e:
        return False



def get_or_create(session, model, defaults=None, **kwargs):
    """
    :param session:
    :param model:
    :param defaults:
    :param kwargs:
    :return: tuple (instance, boolean: if instance is created)
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = {**kwargs, **(defaults or {})}
        instance = model(**params)
        session.add(instance)
        # Do not flush or commit here
        return instance, True


@click.command("generate-products", short_help="Generate products from JSON file.")
@click.option("--file", default="uploads/products.json", help="Path to the standardized JSON data file.")
@click.option("--clear", default=True, is_flag=True, help="Clear Product, Ingredient, ProductIngredient, Brand, Category tables before generating.")
@with_appcontext
def generate_products(file, clear):
    """
    Example:
    flask generate-products --file path/to/your/data.json
    flask generate-products --file path/to/data.json --clear
    """

    file_path = file
    click.echo(f"Reading data from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
    except Exception as e:
        click.echo(f"Error reading file '{file_path}': {e}")
        return

    if not isinstance(products_data, list):
         click.echo(f"Error: JSON file content must be a list of products.")
         return

    session = db.session

    if clear:
        click.echo("Clearing ProductIngredient, Product, Ingredient, Brand, Category tables...")
        try:
            # remove products image
            if os.path.exists(SERVER_IMAGE_STORAGE_DIR):
                # The cho no nhanh :))
                os.system(f'rm -rf {SERVER_IMAGE_STORAGE_DIR}')
            num_assoc_deleted = session.query(ProductIngredient).delete()
            num_prod_deleted = session.query(Product).delete()
            num_ingr_deleted = session.query(Ingredient).delete()
            num_brand_deleted = session.query(Brand).delete()
            num_cat_deleted = session.query(Category).delete()

            session.commit()

            click.echo(f"  - Deleted {num_assoc_deleted} product-ingredient associations.")
            click.echo(f"  - Deleted {num_prod_deleted} products.")
            click.echo(f"  - Deleted {num_ingr_deleted} ingredients.")
            click.echo(f"  - Deleted {num_brand_deleted} brands.")
            click.echo(f"  - Deleted {num_cat_deleted} categories.")
            click.echo("Tables cleared successfully.")
        except Exception as e:
            session.rollback()
            click.echo(f"Error cleaning tables: {e}")
            return

    click.echo(f"Populating database with {len(products_data)} products from '{os.path.basename(file_path)}'...")

    product_count = 0
    added_count = 0
    skipped_existing_count = 0
    skipped_missing_data_count = 0
    error_count = 0

    # Cache objects
    brand_map = {brand.name: brand for brand in session.query(Brand).all()}
    category_map = {cat.name: cat for cat in session.query(Category).all()}
    ingredient_map = {ing.name: ing for ing in session.query(Ingredient).all()}

    for prod_data in products_data:
        product_count += 1
        product_name = prod_data.get('name')
        brand_name = prod_data.get('brand')
        category_name = prod_data.get('category')

        if not product_name:
            click.echo(f"Product {product_count}: Skipping due to missing name.")
            skipped_missing_data_count += 1
            continue

        click.echo(f"Processing product {product_count}: {product_name}")

        # --- Validate data ---
        if not brand_name or brand_name == 'N/A':
            click.echo(f"  > Warning: Missing brand for '{product_name}'. Skipping.")
            skipped_missing_data_count += 1
            continue
        if not category_name or category_name == 'Unknown':
            click.echo(f"  > Warning: Missing or unknown category for '{product_name}'. Skipping.")
            skipped_missing_data_count += 1
            continue
        if prod_data.get('package_quantity') is None or prod_data.get('package_unit') is None:
             click.echo(f"  > Warning: Missing package quantity or unit for '{product_name}'. Skipping.")
             skipped_missing_data_count += 1
             continue
        if prod_data.get('serving_quantity') is None or prod_data.get('serving_unit') is None:
             click.echo(f"  > Warning: Missing serving quantity or unit for '{product_name}'. Skipping.")
             skipped_missing_data_count += 1
             continue

        # --- Start transaction ---
        try:
            # Select or create Brand from cache/DB
            brand = brand_map.get(brand_name)
            if not brand:
                 brand, created = get_or_create(session, Brand, name=brand_name)
                 if created:
                     session.flush()
                     brand_map[brand_name] = brand
                     click.echo(f"    + Created new brand: '{brand_name}'")

            # Select opr create Category from cache/DB
            category = category_map.get(category_name)
            if not category:
                 category, created = get_or_create(session, Category, name=category_name)
                 if created:
                     session.flush()
                     category_map[category_name] = category
                     click.echo(f"    + Created new category: '{category_name}'")

            # Check existing_product
            existing_product = session.query(Product.id).filter_by(name=product_name, brand_id=brand.id).first()
            if existing_product:
                 click.echo(f"  > Product '{product_name}' by '{brand_name}' already exists. Skipping.")
                 skipped_existing_count += 1
                 continue # Bỏ qua nếu đã có

            # Create
            new_product = Product(
                name=product_name,
                price=prod_data.get('price', 0),
                desc=prod_data.get('desc'),
                image_url=prod_data.get('image_url'),
                package_quantity=prod_data.get('package_quantity'),
                package_unit=prod_data.get('package_unit'),
                serving_quantity=prod_data.get('serving_quantity'),
                serving_unit=prod_data.get('serving_unit'),
                brand_id=brand.id,
                category_id=category.id
            )

            # image url
            if new_product.image_url is not None:
                old_url = prod_data.get('image_url')
                download_url = f"{SERVER_IMAGE_STORAGE_DIR}/{old_url.split('/')[-1]}"
                new_url = f"{SERVER_IMAGE_UPLOAD_URL}/{old_url.split('/')[-1]}"
                if download_img(old_url, download_url):
                    new_product.image_url = new_url

            session.add(new_product)
            session.flush() # Flush để new_product có ID cho association
            click.echo(f"    * Added product: '{product_name}'")

            # Ingredients
            ingredients_data = prod_data.get('ingredients', [])
            if ingredients_data:
                 click.echo(f"    > Processing {len(ingredients_data)} ingredients...")
                 for ing_data in ingredients_data:
                    ing_name = ing_data.get('name')
                    ing_quantity = ing_data.get('quantity_per_serving')

                    if not ing_name:
                        click.echo("      - Skipping ingredient with missing name.")
                        continue
                    if ing_quantity is None:
                         click.echo(f"      - Skipping ingredient '{ing_name}' due to missing quantity.")
                         continue

                    # Select or create Ingredient from cache/DB
                    ingredient = ingredient_map.get(ing_name)
                    if not ingredient:
                         ingredient, created = get_or_create(session, Ingredient, name=ing_name)
                         if created:
                             session.flush()
                             ingredient_map[ing_name] = ingredient
                             click.echo(f"      + Created new ingredient: '{ing_name}'")

                    # ProductIngredient association
                    try:
                        assoc = ProductIngredient(
                            product_id=new_product.id,
                            ingredient_id=ingredient.id,
                            quantity=float(ing_quantity)
                        )
                        session.add(assoc)
                        click.echo(f"      - Linked: {ing_name} ({ing_quantity})")
                    except ValueError:
                         click.echo(f"      - Error: Invalid quantity '{ing_quantity}' for ingredient '{ing_name}'. Skipping association.")
                         # Do not roll back here (not commit yet)

            session.commit()
            added_count += 1

        except IntegrityError as e:
            session.rollback()
            click.echo(f"  > DB Integrity Error (e.g., constraint violation): Skipping '{product_name}'. Error: {e.orig}")
            error_count += 1
        except Exception as e:
            session.rollback()
            click.echo(f"  > Unexpected error processing product '{product_name}': {e}")
            import traceback
            traceback.print_exc()
            error_count += 1

    click.echo("\n--- Population Summary ---")
    click.echo(f"Total products in JSON: {product_count}")
    click.echo(f"Successfully added:     {added_count}")
    click.echo(f"Skipped (already exist):{skipped_existing_count}")
    click.echo(f"Skipped (missing data): {skipped_missing_data_count}")
    click.echo(f"Errors during process:  {error_count}")
    click.echo("--------------------------")