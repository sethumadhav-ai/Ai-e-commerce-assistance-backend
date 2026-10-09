from random import Random
from sqlalchemy.orm import Session

from database import engine
from app.models.category import Category
from app.models.product import Product


random = Random(42)


CATALOG = {
    "Laptops": {
        "brands": ["Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI", "Apple", "Microsoft"],
        "models": [
            "Inspiron", "Latitude", "Vostro", "XPS",
            "ProBook", "EliteBook", "Pavilion",
            "ThinkPad", "IdeaPad", "Yoga",
            "VivoBook", "ZenBook", "ROG",
            "Swift", "Aspire", "MacBook Air",
            "MacBook Pro", "Surface Laptop"
        ],
        "features": [
            "Intel Core i5",
            "Intel Core i7",
            "Intel Core i9",
            "AMD Ryzen 5",
            "AMD Ryzen 7",
            "AMD Ryzen 9",
            "Apple M3"
        ],
        "sizes": ["13.3-inch", "14-inch", "15.6-inch", "16-inch"],
        "price": (450, 3500),
        "tags": "laptop,computer,notebook,productivity"
    },

    "Smartphones": {
        "brands": [
            "Samsung", "Apple", "Google", "OnePlus",
            "Xiaomi", "Motorola", "Nothing", "Realme",
            "Oppo", "Vivo"
        ],
        "models": [
            "Galaxy S", "Galaxy A", "iPhone",
            "Pixel", "Nord", "Redmi",
            "Moto Edge", "Nothing Phone",
            "Reno", "Find X", "V Series"
        ],
        "features": [
            "5G",
            "AMOLED",
            "120Hz display",
            "OIS camera",
            "fast charging",
            "wireless charging"
        ],
        "sizes": ["128GB", "256GB", "512GB", "1TB"],
        "price": (150, 2200),
        "tags": "smartphone,mobile,5G,android,ios"
    },

    "Tablets": {
        "brands": [
            "Apple", "Samsung", "Lenovo",
            "Xiaomi", "OnePlus", "Microsoft", "Amazon"
        ],
        "models": [
            "iPad", "iPad Air", "iPad Pro",
            "Galaxy Tab", "Tab P",
            "Pad", "Surface Go", "Fire HD"
        ],
        "features": [
            "Wi-Fi",
            "5G",
            "stylus support",
            "120Hz display",
            "keyboard support",
            "high resolution display"
        ],
        "sizes": [
            "8-inch", "10.1-inch", "11-inch",
            "12.4-inch", "13-inch"
        ],
        "price": (120, 1800),
        "tags": "tablet,portable,stylus,productivity"
    },

    "Headphones": {
        "brands": [
            "Sony", "Bose", "JBL", "Sennheiser",
            "Apple", "Anker", "Audio-Technica",
            "Beats", "Marshall"
        ],
        "models": [
            "WH Series", "QuietComfort",
            "Tune", "Momentum",
            "AirPods", "Soundcore",
            "ATH", "Major"
        ],
        "features": [
            "Active Noise Cancellation",
            "Bluetooth 5.3",
            "Hi-Res Audio",
            "multipoint",
            "low latency",
            "spatial audio"
        ],
        "sizes": [
            "over-ear",
            "on-ear",
            "wireless",
            "true wireless"
        ],
        "price": (25, 650),
        "tags": "headphones,audio,bluetooth,wireless"
    },

    "Monitors": {
        "brands": [
            "LG", "Samsung", "Dell", "ASUS",
            "Acer", "BenQ", "MSI", "AOC"
        ],
        "models": [
            "UltraGear", "Odyssey", "UltraSharp",
            "ProArt", "Nitro", "DesignVue",
            "MAG", "AGON"
        ],
        "features": [
            "IPS",
            "OLED",
            "HDR",
            "USB-C",
            "adaptive sync",
            "4K resolution",
            "144Hz refresh rate"
        ],
        "sizes": [
            "24-inch", "27-inch",
            "32-inch", "34-inch", "49-inch"
        ],
        "price": (100, 2500),
        "tags": "monitor,display,gaming,office"
    },

    "Keyboards": {
        "brands": [
            "Logitech", "Keychron", "Razer",
            "Corsair", "Microsoft", "Dell",
            "HP", "ASUS"
        ],
        "models": [
            "K Series", "MX Keys",
            "BlackWidow", "K70",
            "Surface Keyboard",
            "Mechanical Pro"
        ],
        "features": [
            "mechanical",
            "wireless",
            "RGB",
            "hot-swappable",
            "low-profile",
            "Bluetooth"
        ],
        "sizes": [
            "60%", "65%", "75%",
            "TKL", "full-size"
        ],
        "price": (25, 350),
        "tags": "keyboard,mechanical,rgb,wireless"
    },

    "Mice": {
        "brands": [
            "Logitech", "Razer", "Corsair",
            "SteelSeries", "Microsoft",
            "Dell", "HP", "ASUS"
        ],
        "models": [
            "MX Master", "G Pro",
            "DeathAdder", "Basilisk",
            "Aerox", "Harpoon", "Ergo"
        ],
        "features": [
            "wireless",
            "ergonomic",
            "RGB",
            "high precision sensor",
            "silent clicks",
            "programmable buttons"
        ],
        "sizes": [
            "compact", "medium",
            "large", "ergonomic"
        ],
        "price": (15, 220),
        "tags": "mouse,wireless,gaming,ergonomic"
    },

    "Smartwatches": {
        "brands": [
            "Apple", "Samsung", "Garmin",
            "Fitbit", "Amazfit",
            "OnePlus", "Huawei", "Noise"
        ],
        "models": [
            "Watch Series", "Galaxy Watch",
            "Venu", "Forerunner",
            "Versa", "GTR", "Watch"
        ],
        "features": [
            "GPS",
            "heart-rate tracking",
            "sleep tracking",
            "water resistant",
            "AMOLED",
            "blood oxygen tracking"
        ],
        "sizes": [
            "40mm", "42mm",
            "44mm", "46mm", "47mm"
        ],
        "price": (45, 1000),
        "tags": "smartwatch,fitness,gps,wearable"
    },

    "Cameras": {
        "brands": [
            "Sony", "Canon", "Nikon",
            "Fujifilm", "Panasonic",
            "GoPro", "DJI", "OM System"
        ],
        "models": [
            "Alpha", "EOS", "Z Series",
            "X Series", "Lumix",
            "HERO", "Osmo", "OM"
        ],
        "features": [
            "4K video",
            "8K video",
            "image stabilization",
            "Wi-Fi",
            "fast autofocus",
            "high resolution sensor"
        ],
        "sizes": [
            "mirrorless",
            "DSLR",
            "action camera",
            "compact"
        ],
        "price": (200, 5000),
        "tags": "camera,photography,video,4K"
    },

    "Televisions": {
        "brands": [
            "Samsung", "LG", "Sony", "TCL",
            "Hisense", "OnePlus",
            "Panasonic", "Xiaomi"
        ],
        "models": [
            "Neo QLED", "OLED",
            "Bravia", "QLED",
            "Mini LED", "U Series",
            "Smart TV"
        ],
        "features": [
            "4K",
            "8K",
            "HDR10+",
            "Dolby Vision",
            "120Hz",
            "Dolby Atmos"
        ],
        "sizes": [
            "43-inch",
            "50-inch",
            "55-inch",
            "65-inch",
            "75-inch",
            "85-inch"
        ],
        "price": (250, 6000),
        "tags": "television,4K,smart-tv,home-entertainment"
    },

    "Gaming": {
        "brands": [
            "Sony", "Microsoft", "Nintendo",
            "ASUS", "Razer", "Logitech",
            "Corsair", "MSI"
        ],
        "models": [
            "PlayStation", "Xbox",
            "Switch", "ROG",
            "BlackShark", "G Series",
            "Scuf", "MAG"
        ],
        "features": [
            "4K gaming",
            "120Hz",
            "wireless",
            "RGB",
            "low latency",
            "ray tracing"
        ],
        "sizes": [
            "standard", "pro",
            "elite", "wireless"
        ],
        "price": (40, 2500),
        "tags": "gaming,console,pc-gaming,accessories"
    },

    "Accessories": {
        "brands": [
            "Anker", "Belkin", "UGREEN",
            "Spigen", "Baseus",
            "Logitech", "Samsung", "Apple"
        ],
        "models": [
            "PowerHub", "ChargePro",
            "UltraCable", "MagSafe",
            "TechStand", "Connect", "Flex"
        ],
        "features": [
            "USB-C",
            "fast charging",
            "GaN",
            "multi-port",
            "portable",
            "wireless charging"
        ],
        "sizes": [
            "compact",
            "standard",
            "multi-port",
            "travel"
        ],
        "price": (10, 300),
        "tags": "accessories,charger,cable,usb-c,technology"
    }
}


def get_or_create_category(db, name):
    category = (
        db.query(Category)
        .filter(Category.name == name)
        .first()
    )

    if category:
        return category

    category = Category(
        name=name,
        description=f"{name} products"
    )

    db.add(category)
    db.flush()

    return category


def product_exists(db, name):
    return (
        db.query(Product)
        .filter(Product.name == name)
        .first()
        is not None
    )


def generate_product_name(brand, model, feature, size, number):
    return (
        f"{brand} {model} "
        f"{feature} {size} "
        f"Edition {number}"
    )


def seed_products(products_per_category=60):

    db = Session(bind=engine)

    added = 0
    skipped = 0

    try:

        for category_name, data in CATALOG.items():

            category = get_or_create_category(
                db,
                category_name
            )

            for number in range(
                1,
                products_per_category + 1
            ):

                brand = random.choice(
                    data["brands"]
                )

                model = random.choice(
                    data["models"]
                )

                feature = random.choice(
                    data["features"]
                )

                size = random.choice(
                    data["sizes"]
                )

                name = generate_product_name(
                    brand,
                    model,
                    feature,
                    size,
                    number
                )

                if product_exists(db, name):
                    skipped += 1
                    continue

                min_price, max_price = data["price"]

                price = random.randint(
                    min_price,
                    max_price
                )

                rating = round(
                    random.uniform(3.5, 5.0),
                    1
                )

                stock = random.randint(
                    5,
                    150
                )

                description = (
                    f"{name} is a high-quality "
                    f"{category_name.lower()} product "
                    f"from {brand}. "
                    f"It is designed for reliable "
                    f"everyday performance and "
                    f"modern user requirements. "
                    f"The product includes "
                    f"{feature} and comes in a "
                    f"{size} configuration."
                )

                specifications = (
                    f"Brand: {brand}; "
                    f"Model: {model}; "
                    f"Feature: {feature}; "
                    f"Size: {size}; "
                    f"Category: {category_name}"
                )

                tags = (
                    f"{data['tags']},"
                    f"{brand.lower()},"
                    f"{feature.lower().replace(' ', '-')}"
                )

                product = Product(
                    name=name,
                    description=description,
                    brand=brand,
                    price=price,
                    stock=stock,
                    rating=rating,
                    category_id=category.id,
                    specifications=specifications,
                    tags=tags,
                    image_url=None,
                    is_active=True
                )

                db.add(product)

                added += 1

        db.commit()

        print()
        print("=" * 50)
        print("PRODUCT SEEDING COMPLETED")
        print("=" * 50)
        print(f"Products added  : {added}")
        print(f"Products skipped : {skipped}")
        print(f"Categories       : {len(CATALOG)}")
        print(
            f"Target products/category : "
            f"{products_per_category}"
        )
        print(
            f"Maximum new products this run : "
            f"{len(CATALOG) * products_per_category}"
        )
        print("=" * 50)

    except Exception as e:

        db.rollback()

        print()
        print("ERROR while seeding products:")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_products(60)