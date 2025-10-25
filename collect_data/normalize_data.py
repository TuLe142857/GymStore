import json
import re
import os

def clean_price(price_text) -> int:
    if price_text is None: return 0
    if isinstance(price_text, (int, float)): return int(price_text)
    if not isinstance(price_text, str): return 0
    nums = re.sub(r'\D', '', price_text)
    try:
        return int(nums)
    except (ValueError, TypeError):
        return 0


def parse_package_info(weight_text)-> tuple[float, str] | tuple[None, None]:
    if not isinstance(weight_text, str): return None, None
    quantity, unit = None, None
    weight_text_lower = weight_text.lower().replace(',', '.')
    try:
        kg_match = re.search(r'([\d.]+)\s*kg', weight_text_lower)
        lbs_match = re.search(r'([\d.]+)\s*lbs', weight_text_lower)
        vien_match = re.search(r'(\d+)\s*viên', weight_text_lower)
        g_match = re.search(r'([\d.]+)\s*g', weight_text_lower)
        ml_match = re.search(r'([\d.]+)\s*ml', weight_text_lower)
        thanh_match = re.search(r'(\d+)\s*thanh', weight_text_lower)  # Thêm thanh

        if kg_match:
            quantity, unit = float(kg_match.group(1)), 'kg'
        elif lbs_match:
            quantity, unit = float(lbs_match.group(1)), 'lbs'
        elif vien_match:
            quantity, unit = int(vien_match.group(1)), 'viên'
        elif thanh_match:
            quantity, unit = int(thanh_match.group(1)), 'thanh'
        elif g_match:
            quantity, unit = float(g_match.group(1)), 'g'
        elif ml_match:
            quantity, unit = float(ml_match.group(1)), 'ml'
        elif not unit:
            num_match = re.search(r'([\d.]+)', weight_text_lower)
            if num_match: quantity, unit = float(num_match.group(1)), 'unknown'
    except (AttributeError, ValueError, TypeError):
        quantity, unit = None, None
    if isinstance(quantity, float): quantity = round(quantity, 2)
    return quantity, unit


def parse_serving_info(serving_text)->tuple[float, str] | tuple[None, None]:
    if not isinstance(serving_text, str): return None, None
    quantity, unit = None, None
    serving_text_lower = serving_text.lower().replace(',', '.')
    try:
        vien_match = re.search(r'(\d+)\s*viên', serving_text_lower)
        muong_match = re.search(r'([\d.]+)\s*muỗng', serving_text_lower)
        goi_match = re.search(r'(\d+)\s*gói', serving_text_lower)
        thanh_match = re.search(r'(\d+)\s*thanh', serving_text_lower)
        g_match_paren = re.search(r'\((\d+)\s*g\)', serving_text_lower)
        g_match_simple = re.search(r'([\d.]+)\s*g', serving_text_lower)
        ml_match = re.search(r'([\d.]+)\s*ml', serving_text_lower)

        if vien_match:
            quantity, unit = int(vien_match.group(1)), 'viên'
        elif muong_match:
            quantity, unit = float(muong_match.group(1)), 'muỗng'
        elif goi_match:
            quantity, unit = int(goi_match.group(1)), 'gói'
        elif thanh_match:
            quantity, unit = int(thanh_match.group(1)), 'thanh'
        elif g_match_paren:
            quantity, unit = int(g_match_paren.group(1)), 'g'
        elif g_match_simple and not unit:
            quantity, unit = float(g_match_simple.group(1)), 'g'
        elif ml_match and not unit:
            quantity, unit = float(ml_match.group(1)), 'ml'
        elif not unit:
            num_match = re.search(r'([\d.]+)', serving_text_lower)
            if num_match: quantity, unit = float(num_match.group(1)), 'unknown'
    except (AttributeError, ValueError, TypeError):
        quantity, unit = None, None
    if isinstance(quantity, float):
        if quantity.is_integer():
            quantity = int(quantity)
        else:
            quantity = round(quantity, 2)

    return quantity, unit

def parse_quantity_unit(value_str):
    """Trích xuất (quantity, unit) từ chuỗi như '25g', '5.5g', '110 -120 calories', '5mg'."""
    if not isinstance(value_str, str): return None, None

    # Ưu tiên tìm số và đơn vị liền kề (5g, 10mg, 100kcal)
    match_direct = re.search(r'([\d.]+)\s*([a-zA-Zμ]+)\b', value_str)  # Thêm μ cho mcg
    if match_direct:
        try:
            quantity = float(match_direct.group(1))
            unit = match_direct.group(2).lower()
            # Chuẩn hóa đơn vị calories
            if 'kcal' in unit or 'calories' in unit:
                unit = 'kcal'
            elif 'mcg' in unit or 'μg' in unit:
                unit = 'mcg'
            elif unit == 'grams':
                unit = 'g'

            if quantity % 1 == 0: quantity = int(quantity)  # Chuyển thành int nếu là số nguyên
            return quantity, unit
        except ValueError:
            pass  # Bỏ qua nếu không parse được số

    # Nếu không tìm thấy, thử tìm số đầu tiên (cho trường hợp như '110 -120 calories')
    match_first_num = re.search(r'([\d.]+)', value_str)
    if match_first_num:
        try:
            quantity = float(match_first_num.group(1))
            # Đoán đơn vị từ text
            unit = None
            if 'kcal' in value_str.lower() or 'calories' in value_str.lower():
                unit = 'kcal'
            elif 'mg' in value_str.lower():
                unit = 'mg'
            elif 'mcg' in value_str.lower() or 'μg' in value_str.lower():
                unit = 'mcg'
            elif 'g' in value_str.lower():
                unit = 'g'

            if quantity % 1 == 0: quantity = int(quantity)
            return quantity, unit
        except ValueError:
            return None, None

    return None, None  # Không tìm thấy gì


def parse_ingredients(details_dict):
    """Trích xuất danh sách thành phần từ dictionary details."""
    ingredients = []
    processed_keys = set()  # Theo dõi các key đã xử lý để tránh trùng lặp

    # 1. Ưu tiên xử lý các key hàm lượng cụ thể
    key_map = {
        'hàm lượng protein': 'Protein',
        'hàm lượng bcaa': 'BCAA',
        'calories': 'Calories'
    }
    for key_vi, name_en in key_map.items():
        for detail_key, detail_value in details_dict.items():
            if key_vi in detail_key.lower() and detail_key not in processed_keys:
                quantity, unit = parse_quantity_unit(detail_value)
                if quantity is not None:
                    ingredients.append({
                        "name": name_en,
                        "quantity_per_serving": quantity,
                        "unit": unit
                    })
                    processed_keys.add(detail_key)
                    break  # Chỉ lấy giá trị đầu tiên khớp

    # 2. Xử lý key "Thành phần" và "Thành phần khác"
    generic_ingredient_keys = ['thành phần', 'thành phần khác']
    for generic_key in generic_ingredient_keys:
        for detail_key, detail_value in details_dict.items():
            if generic_key in detail_key.lower() and detail_key not in processed_keys:
                if not isinstance(detail_value, str): continue

                # Tách chuỗi thành các thành phần con dựa trên dấu phẩy, chấm phẩy, xuống dòng
                parts = re.split(r'[;,|\n]', detail_value)

                for part in parts:
                    part_cleaned = part.strip()
                    if not part_cleaned: continue

                    quantity, unit = parse_quantity_unit(part_cleaned)

                    if quantity is not None and unit is not None:
                        # Nếu có số lượng và đơn vị, phần còn lại là tên
                        # Cố gắng loại bỏ số lượng và đơn vị khỏi tên
                        name_guess = re.sub(r'([\d.]+)\s*([a-zA-Zμ]+)\b', '', part_cleaned, count=1).strip()
                        # Dọn dẹp tên thêm (loại bỏ dấu hai chấm, dấu gạch ngang ở đầu/cuối)
                        name_guess = re.sub(r'^[-\:]+\s*|\s*[-\:]+$', '', name_guess).strip()
                        if not name_guess:  # Nếu tên trống, có thể chỉ là dạng "5g Citrulline Malate"
                            name_guess = re.sub(r'([\d.]+)\s*[a-zA-Zμ]+\s*', '',
                                                part_cleaned).strip()  # Lấy phần text còn lại

                        if name_guess:  # Chỉ thêm nếu có tên
                            ingredients.append({
                                "name": name_guess.capitalize(),  # Viết hoa chữ đầu
                                "quantity_per_serving": quantity,
                                "unit": unit
                            })
                    else:
                        # Nếu không có số lượng/đơn vị rõ ràng, coi cả chuỗi là tên
                        # Bỏ qua các chuỗi quá dài hoặc có vẻ không phải tên thành phần
                        if len(part_cleaned) < 50 and not part_cleaned.lower().startswith(
                                ('ảnh:', 'pha', 'ngày', 'lưu ý', 'cảnh báo')):
                            ingredients.append({
                                "name": part_cleaned.capitalize(),
                                "quantity_per_serving": None,
                                "unit": None
                            })
                processed_keys.add(detail_key)
                break  # Chỉ xử lý key "Thành phần" / "Thành phần khác" đầu tiên tìm thấy

    # 3. Loại bỏ trùng lặp (dựa trên tên, giữ cái có quantity/unit nếu có thể)
    final_ingredients = {}
    for ing in ingredients:
        name_lower = ing['name'].lower()
        existing = final_ingredients.get(name_lower)
        if not existing:
            final_ingredients[name_lower] = ing
        # Ưu tiên giữ lại entry có quantity và unit
        elif ing['quantity_per_serving'] is not None and ing['unit'] is not None and \
                (existing['quantity_per_serving'] is None or existing['unit'] is None):
            final_ingredients[name_lower] = ing
        # Hoặc nếu entry mới có quantity/unit còn entry cũ thì không
        elif (ing['quantity_per_serving'] is not None or ing['unit'] is not None) and \
                (existing['quantity_per_serving'] is None and existing['unit'] is None):
            final_ingredients[name_lower] = ing

    return list(final_ingredients.values())


# --- LOGIC CHÍNH ---

def standardize_data(input_filename="data.json", output_filename="data.json"):
    """Đọc file JSON đầu vào, chuẩn hóa và ghi ra file JSON mới."""

    input_filepath = os.path.join(os.path.dirname(__file__), input_filename)
    output_filepath = os.path.join(os.path.dirname(__file__), output_filename)

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{input_filepath}'")
        return
    except json.JSONDecodeError:
        print(f"Lỗi: File '{input_filepath}' không phải là JSON hợp lệ.")
        return
    except Exception as e:
        print(f"Lỗi không xác định khi đọc file '{input_filepath}': {e}")
        return

    standardized_products = []
    print(f"Bắt đầu chuẩn hóa {len(raw_data)} sản phẩm từ '{input_filename}'...")

    processed_count = 0
    skipped_count = 0

    for product in raw_data:
        processed_count += 1
        print(f"\nProcessing product {processed_count}: {product.get('name', 'N/A')}")

        details = product.get('details', {})
        std_product = {
            'name': product.get('name', 'N/A'),
            'price': clean_price(product.get('price')),
            'desc': product.get('desc', 'N/A'),
            'image_url': product.get('img_url', 'N/A'),
            'brand': 'N/A',
            'category': product.get('category',None),
            'package_quantity': None,
            'package_unit': None,
            'serving_quantity': None,
            'serving_unit': None,
            'origin': 'N/A',
            'source_url': product.get('scraped_from_url', 'N/A'),
            'ingredients': []  # <-- Thêm trường ingredients
        }

        # Xử lý trường details để lấy thông tin cơ bản
        weight_found = False
        serving_found = False

        for key, value in details.items():
            key_lower = key.lower()
            if not weight_found and ('trọng lượng' in key_lower or 'weight' in key_lower or 'định lượng' in key_lower):
                std_product['package_quantity'], std_product['package_unit'] = parse_package_info(value)
                if std_product['package_quantity'] is not None: weight_found = True
            elif not serving_found and ('serving size' in key_lower):
                std_product['serving_quantity'], std_product['serving_unit'] = parse_serving_info(value)
                if std_product['serving_quantity'] is not None: serving_found = True
            elif 'thương hiệu' in key_lower or 'brand' in key_lower:
                std_product['brand'] = value.strip()
            elif 'xuất xứ' in key_lower or 'origin' in key_lower:
                std_product['origin'] = value.strip()

        # --- Trích xuất Ingredients từ details ---
        std_product['ingredients'] = parse_ingredients(details)

        # Kiểm tra các trường quan trọng (bỏ qua nếu thiếu)
        if not std_product['package_quantity'] or not std_product['package_unit'] or \
                not std_product['serving_quantity'] or not std_product['serving_unit']:

            if not (std_product['serving_quantity'] == 1 and std_product['serving_unit'] in ['thanh', 'gói', 'viên',
                                                                                             'lon']):
                print(
                    f"  >> Cảnh báo: Thiếu thông tin package hoặc serving cho '{std_product['name']}'. Bỏ qua sản phẩm này.")
                skipped_count += 1
                continue

        print(f"  > Standardized: Brand='{std_product['brand']}', Category='{std_product['category']}', "
              f"Package={std_product['package_quantity']} {std_product['package_unit']}, "
              f"Serving={std_product['serving_quantity']} {std_product['serving_unit']}")
        print(f"  > Ingredients Found: {len(std_product['ingredients'])}")  # In số lượng thành phần

        standardized_products.append(std_product)


    if standardized_products:
        print(
            f"\nNormalized {len(standardized_products)} product{"s" if len(standardized_products) > 1 else ""}({skipped_count} product{"s" if skipped_count>1 else "" } skipped).")
    else:
        print("\nNo products were normalized.")

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(standardized_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to '{output_filename}'")

if __name__ == "__main__":
    standardize_data(input_filename="collected_data.json", output_filename="products.json")
