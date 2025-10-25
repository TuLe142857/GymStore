import requests
from bs4 import BeautifulSoup
import json
import traceback
import time

def get(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        raise e

def scan_product_link(url)->list[str]|None:
    try:
        page = get(url)
        url_list = []
        product_card = page.find_all(class_='itproduct')
        for p in product_card:
            link = p.find('a')
            if link is not None and link.has_attr('href'):
                url_list.append(link.get('href'))
        return url_list
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None

def get_product_detail_on_page(url):
    try:
        res = dict()
        page = get(url)

        res['name'] = page.find(class_='name_products').text.strip()

        res['price'] =  int(page.find(id='price').text.strip().replace(".", "").replace("₫", ""))

        desc = page.find(id='boxdesc').find_all('p')
        desc = [_.text.strip() for _ in desc]
        desc = "\n".join(desc)
        res['desc'] = desc

        details_ = page.find(class_='all_products_compare').find_all('tr')
        details = dict()
        for d in details_:
            td = d.find_all("td")
            details[td[0].text.strip()] = " ".join(td[1].text.strip().replace('\t', ' ').split())

        res['details'] = details

        imgs = page.find_all('img')
        href = [_.get('src') for _ in imgs if _.has_attr('src') and 'product' in _.get('src')]
        img=None
        if href:
            img = href[0]
        res['img_url'] = img

        return res
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


if __name__ == "__main__":
    OUTPUT = "collected_data.json"

    links = [
        {
            "url": "https://www.wheystore.vn/whey-protein-c1",
            "category": "Whey Protein"
        },
        {
            "url": "https://www.wheystore.vn/mass-gainer-c2",
            "category": "Mass Gainer"
        },
        {
            "url": "https://www.wheystore.vn/bcaa-eaa-amino-acid-c11",
            "category": "Amino Acid"
        },
        {
            "url": "https://www.wheystore.vn/tang-suc-manh-c16",
            "category": "Pre-Workout"
        }
    ]

    products = []
    for link in links:
        urls = scan_product_link(link['url'])
        if urls is None:
            print(f"Can not scan from  {link['url']}")
            continue
        print(f"From {link['url']}: ")

        for url in urls:
            product = get_product_detail_on_page(url)
            if product is None:
                print(f"\tCan not scan from  {url}")
                continue

            product['category'] = link['category']
            products.append(product)

            print(f"\tFrom {url}: ok - {product['name']}")
            # print(json.dumps(product, indent=4, ensure_ascii=False))

            time.sleep(0.2)


    print(f"\n\nFinished, n_product collected = {len(products)}")

    with open(OUTPUT, "w") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"Writing data to file '{OUTPUT}' completed !")