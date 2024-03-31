from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


User = get_user_model()
Store = apps.get_model('stores', 'Store')
Fandom = apps.get_model('fandoms', 'Fandom')
Character = apps.get_model('fandoms', 'Character')
Product = apps.get_model('products', 'Product')
ProductImage = apps.get_model('products', 'ProductImage')


class Command(BaseCommand):
    help = 'Initialize db with some data'

    def handle(self, *args, **options):
        if not Store.objects.count():
            users_data = [
                {
                    'username': 'scala',
                    'email': 'scala@example.com',
                    'password': make_password('password123')
                },
                {
                    'username': 'babyboom',
                    'email': 'babyboom@example.com',
                    'password': make_password('password234')
                },
                {
                    'username': 'mega_brain',
                    'email': 'mega_brain@example.com',
                    'password': make_password('password345')
                },
                {
                    'username': 'jackychany',
                    'email': 'jackychany@example.com',
                    'password': make_password('password456')
                },
                {
                    'username': 'golden_cupcake',
                    'email': 'golden_cupcake@example.com',
                    'password': make_password('password567')
                },
                {
                    'username': 'neon_ninja',
                    'email': 'neon_ninja@example.com',
                    'password': make_password('password678')
                },
                {
                    'username': 'pixel_pirate',
                    'email': 'pixel_pirate@example.com',
                    'password': make_password('password789')
                },
                {
                    'username': 'cyber_samurai',
                    'email': 'cyber_samurai@example.com',
                    'password': make_password('password890')
                },
                {
                    'username': 'lunar_lion',
                    'email': 'lunar_lion@example.com',
                    'password': make_password('password901')
                }
            ]

            for user_data in users_data:
                User.objects.create(**user_data)

            stores_data = [
                {
                    'owner': User.objects.get(username='admin'),
                    'name': 'Cosplay Store',
                    'organization_type': 'LLC',
                    'organization_name': 'Cosplay Store LLC',
                    'taxpayer_number': '1234567890',
                    'check_number': '11111111111111111111',
                    'logo': 'store_logos/store_1/cosplay.png',
                    'bio': 'Your one-stop shop for all things cosplay!',
                    'is_verified': 'True',
                    'is_admin_store': 'True'
                },
                {
                    'owner': User.objects.get(username='scala'),
                    'name': 'Superhero Cosplay',
                    'organization_type': 'LLC',
                    'organization_name': 'Superhero Cosplay LLC',
                    'taxpayer_number': '0987654321',
                    'check_number': '22222222222222222222',
                    'logo': 'store_logos/store_2/superhero.jpg',
                    'bio': 'Your favorite superheroes brought to life!',
                    'is_verified': 'True',
                },
                {
                    'owner': User.objects.get(username='babyboom'),
                    'name': 'Fantasy Cosplay Emporium',
                    'organization_type': 'JSC',
                    'organization_name': 'Fantasy Cosplay Emporium JSC',
                    'taxpayer_number': '1357924680',
                    'check_number': '33333333333333333333',
                    'logo': 'store_logos/store_3/fantasy.jpg',
                    'bio': 'Explore realms of magic and wonder!',
                    'is_verified': 'True',
                },
                {
                    'owner': User.objects.get(username='mega_brain'),
                    'name': 'Sci-Fi Cosplay Galaxy',
                    'organization_type': 'IE',
                    'organization_name': 'Sci-Fi Cosplay Galaxy',
                    'taxpayer_number': '9876543210',
                    'check_number': '44444444444444444444',
                    'logo': 'store_logos/store_4/scifi.jpg',
                    'bio': 'Embark on epic journeys to distant worlds!'
                },
                {
                    'owner': User.objects.get(username='jackychany'),
                    'name': 'Anime Lovers',
                    'organization_type': 'SE',
                    'organization_name': 'Anime Lovers Cosplay',
                    'taxpayer_number': '5432167890',
                    'check_number': '55555555555555555555',
                    'logo': 'store_logos/store_5/anime.jpeg',
                    'bio': 'We love anime!'
                }
            ]
            
            for store_data in stores_data:
                Store.objects.create(**store_data)

            fandoms_data = [
                {
                    'name': 'Genshin Impact',
                    'fandom_type': 'Games',
                    'image': 'fandom_images/genshin-impact/genshin_impact.jpg'
                },
                {
                    'name': 'Marvel',
                    'fandom_type': 'Movies',
                    'image': 'fandom_images/marvel/marvel.jpg'
                },
                {
                    'name': 'Chainsaw Man',
                    'fandom_type': 'Anime',
                    'image': 'fandom_images/chainsaw-man/chainsaw_man.jpg'
                },
                {
                    'name': 'Dota 2',
                    'fandom_type': 'Games',
                    'image': 'fandom_images/dota-2/dota_2.jpg'
                },
                {
                    'name': 'Game of Thrones',
                    'fandom_type': 'Series',
                    'image': 'fandom_images/game-of-thrones/game_of_thrones.jpg'
                }
            ]

            for fandom_data in fandoms_data:
                Fandom.objects.create(**fandom_data)

            characters_data = [
                # Genshin Impact
                {
                    'name': 'Diluc',
                    'image': 'character_images/genshin-impact/diluc.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Jean',
                    'image': 'character_images/genshin-impact/jean.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Venti',
                    'image': 'character_images/genshin-impact/venti.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Klee',
                    'image': 'character_images/genshin-impact/klee.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Qiqi',
                    'image': 'character_images/genshin-impact/qiqi.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Mona',
                    'image': 'character_images/genshin-impact/mona.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Keqing',
                    'image': 'character_images/genshin-impact/keqing.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Zhongli',
                    'image': 'character_images/genshin-impact/zhongli.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Xiao',
                    'image': 'character_images/genshin-impact/xiao.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                {
                    'name': 'Hu Tao',
                    'image': 'character_images/genshin-impact/hu_tao.jpg',
                    'fandom': Fandom.objects.get(name='Genshin Impact'),
                },
                # Marvel
                {
                    'name': 'Iron Man',
                    'image': 'character_images/marvel/iron-man.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Captain America',
                    'image': 'character_images/marvel/captain-america.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Thor',
                    'image': 'character_images/marvel/thor.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Hulk',
                    'image': 'character_images/marvel/hulk.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Black Widow',
                    'image': 'character_images/marvel/black-widow.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Spider-Man',
                    'image': 'character_images/marvel/spider-man.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Doctor Strange',
                    'image': 'character_images/marvel/doctor-strange.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Black Panther',
                    'image': 'character_images/marvel/black-panther.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Captain Marvel',
                    'image': 'character_images/marvel/captain-marvel.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                {
                    'name': 'Scarlet Witch',
                    'image': 'character_images/marvel/scarlet-witch.jpg',
                    'fandom': Fandom.objects.get(name='Marvel'),
                },
                # Chainsaw Man
                {
                    'name': 'Denji',
                    'image': 'character_images/chainsaw-man/denji.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Power',
                    'image': 'character_images/chainsaw-man/power.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Makima',
                    'image': 'character_images/chainsaw-man/makima.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Aki Hayakawa',
                    'image': 'character_images/chainsaw-man/aki-hayakawa.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Kishibe',
                    'image': 'character_images/chainsaw-man/kishibe.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Quanxi',
                    'image': 'character_images/chainsaw-man/quanxi.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Beam',
                    'image': 'character_images/chainsaw-man/beam.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Nyako',
                    'image': 'character_images/chainsaw-man/nyako.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Katana Man',
                    'image': 'character_images/chainsaw-man/katana-man.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                {
                    'name': 'Himeno',
                    'image': 'character_images/chainsaw-man/himeno.jpg',
                    'fandom': Fandom.objects.get(name='Chainsaw Man'),
                },
                # Dota 2
                {
                    'name': 'Invoker',
                    'image': 'character_images/dota-2/invoker.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Mirana',
                    'image': 'character_images/dota-2/mirana.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Juggernaut',
                    'image': 'character_images/dota-2/juggernaut.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Pudge',
                    'image': 'character_images/dota-2/pudge.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Crystal Maiden',
                    'image': 'character_images/dota-2/crystal-maiden.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Anti-Mage',
                    'image': 'character_images/dota-2/anti-mage.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Drow Ranger',
                    'image': 'character_images/dota-2/drow-ranger.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Lina',
                    'image': 'character_images/dota-2/lina.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Earthshaker',
                    'image': 'character_images/dota-2/earthshaker.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                {
                    'name': 'Windranger',
                    'image': 'character_images/dota-2/windranger.jpg',
                    'fandom': Fandom.objects.get(name='Dota 2'),
                },
                # Game of Thrones
                {
                    'name': 'Jon Snow',
                    'image': 'character_images/game-of-thrones/jon-snow.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Daenerys Targaryen',
                    'image': 'character_images/game-of-thrones/daenerys-targaryen.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Tyrion Lannister',
                    'image': 'character_images/game-of-thrones/tyrion-lannister.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Arya Stark',
                    'image': 'character_images/game-of-thrones/arya-stark.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Sansa Stark',
                    'image': 'character_images/game-of-thrones/sansa-stark.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Cersei Lannister',
                    'image': 'character_images/game-of-thrones/cersei-lannister.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Jaime Lannister',
                    'image': 'character_images/game-of-thrones/jaime-lannister.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Bran Stark',
                    'image': 'character_images/game-of-thrones/bran-stark.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Sandor Clegane',
                    'image': 'character_images/game-of-thrones/sandor-clegane.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                },
                {
                    'name': 'Petyr Baelish',
                    'image': 'character_images/game-of-thrones/petyr-baelish.jpg',
                    'fandom': Fandom.objects.get(name='Game of Thrones'),
                }
            ]

            for character_data in characters_data:
                Character.objects.create(**character_data)

            products_data = [
                # Genshin Impact Products
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Diluc Full Cosplay Set',
                    'description': 'High-quality Diluc cosplay set including clothes, wig, shoes, and accessories.',
                    'price': 25000,
                    'cosplay_character': Character.objects.get(name='Diluc'),
                    'product_type': 'Full Set',
                    'size': 'M',
                    'in_stock': 10,
                    'discount': 15,
                },
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Jean Cosplay Wig',
                    'description': 'Beautifully crafted Jean wig, perfect for completing your cosplay.',
                    'price': 8000,
                    'cosplay_character': Character.objects.get(name='Jean'),
                    'product_type': 'Wig',
                },
                {
                    'seller': Store.objects.get(name='Fantasy Cosplay Emporium'),
                    'title': 'Venti Cosplay Shoes',
                    'description': 'Comfortable and accurate Venti shoes for your cosplay needs.',
                    'price': 6000,
                    'cosplay_character': Character.objects.get(name='Venti'),
                    'product_type': 'Shoes',
                    'shoes_size': '40',
                    'discount': 10,
                },
                # Marvel Products
                {
                    'seller': Store.objects.get(name='Superhero Cosplay'),
                    'title': 'Iron Man Suit (Replica)',
                    'description': "Detailed replica of Iron Man's iconic suit, perfect for collectors and cosplayers.",
                    'price': 80000,
                    'cosplay_character': Character.objects.get(name='Iron Man'),
                    'product_type': 'Others',
                    'in_stock': 3,
                },
                {
                    'seller': Store.objects.get(name='Superhero Cosplay'),
                    'title': 'Captain America Shield (Prop)',
                    'description': 'Sturdy and realistic Captain America shield prop for cosplay or display.',
                    'price': 15000,
                    'cosplay_character': Character.objects.get(name='Captain America'),
                    'product_type': 'Details',
                    'discount': 20,
                },
                {
                    'seller': Store.objects.get(name='Superhero Cosplay'),
                    'title': 'Black Widow Cosplay Costume',
                    'description': 'High-quality Black Widow costume with accurate details and accessories.',
                    'price': 22000,
                    'cosplay_character': Character.objects.get(name='Black Widow'),
                    'product_type': 'Clothes',
                    'size': 'S',
                },
                # Chainsaw Man Products
                {
                    'seller': Store.objects.get(name='Anime Lovers'),
                    'title': 'Denji Chainsaw Devil Cosplay Set',
                    'description': 'Complete Denji cosplay set featuring his iconic chainsaw devil form.',
                    'price': 30000,
                    'cosplay_character': Character.objects.get(name='Denji'),
                    'product_type': 'Full Set',
                    'size': 'L',
                    'discount': 25,
                },
                {
                    'seller': Store.objects.get(name='Anime Lovers'),
                    'title': 'Power Cosplay Wig and Horns',
                    'description': 'Accurate Power wig with attached horns for a complete cosplay look.',
                    'price': 12000,
                    'cosplay_character': Character.objects.get(name='Power'),
                    'product_type': 'Wig',
                },
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Makima Cosplay Uniform',
                    'description': 'High-quality Makima uniform replica for cosplay enthusiasts.',
                    'price': 18000,
                    'cosplay_character': Character.objects.get(name='Makima'),
                    'product_type': 'Clothes',
                    'size': 'XS',
                    'discount': 10,
                },
                # Dota 2 Products
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Invoker Staff (Prop)',
                    'description': "Detailed replica of Invoker's staff for cosplay or display.",
                    'price': 10000,
                    'cosplay_character': Character.objects.get(name='Invoker'),
                    'product_type': 'Details',
                    'discount': 5,
                },
                {
                    'seller': Store.objects.get(name='Fantasy Cosplay Emporium'),
                    'title': 'Mirana Cosplay Costume and Bow',
                    'description': 'Complete Mirana cosplay set including costume and her signature bow.',
                    'price': 25000,
                    'cosplay_character': Character.objects.get(name='Mirana'),
                    'product_type': 'Full Set',
                    'size': 'M',
                },
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Juggernaut Mask and Armor Set',
                    'description': 'High-quality Juggernaut mask and armor pieces for cosplay.',
                    'price': 32000,
                    'cosplay_character': Character.objects.get(name='Juggernaut'),
                    'product_type': 'Details',
                    'in_stock': 30,
                    'discount': 20,
                },
                # Game of Thrones Products
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Jon Snow Costume and Sword',
                    'description': 'Detailed Jon Snow costume with a replica Longclaw sword.',
                    'price': 28000,
                    'cosplay_character': Character.objects.get(name='Jon Snow'),
                    'product_type': 'Full Set',
                    'size': 'L',
                },
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Daenerys Targaryen Dress and Wig',
                    'description': 'Elegant Daenerys Targaryen dress and wig for cosplay.',
                    'price': 24000,
                    'cosplay_character': Character.objects.get(name='Daenerys Targaryen'),
                    'product_type': 'Clothes',
                    'size': 'S',
                    'discount': 15,
                },
                {
                    'seller': Store.objects.get(name='Cosplay Store'),
                    'title': 'Arya Stark Cosplay Costume',
                    'description': 'Complete Arya Stark costume with her signature Needle sword.',
                    'price': 20000,
                    'cosplay_character': Character.objects.get(name='Arya Stark'),
                    'product_type': 'Full Set',
                    'size': 'XS',
                },
                {
                    "seller": Store.objects.get(name='Cosplay Store'),
                    "title": "Queen Cersei Lannister Costume",
                    "description": "Exquisite costume resembling the attire of Queen Cersei Lannister, adorned with intricate details.",
                    "price": 28000,
                    "cosplay_character": Character.objects.get(name='Cersei Lannister'),
                    "product_type": "Full Set",
                    "size": "L"
                }
            ]

            for product_data in products_data:
                Product.objects.create(**product_data)

            product_images_data = [
                {
                    'product': Product.objects.get(id=1),
                    'image': 'product_images/product_1/diluc_full_set_front.webp'
                },
                {
                    'product': Product.objects.get(id=1),
                    'image': 'product_images/product_1/diluc_full_set_back.webp'
                },
                {
                    'product': Product.objects.get(id=2),
                    'image': 'product_images/product_2/jean_wig.webp'
                },
                {
                    'product': Product.objects.get(id=3),
                    'image': 'product_images/product_3/venti_shoes_1.webp'
                },
                {
                    'product': Product.objects.get(id=3),
                    'image': 'product_images/product_3/venti_shoes_2.webp'
                },
                {
                    'product': Product.objects.get(id=5),
                    'image': 'product_images/product_5/captain_america_shield.jpg'
                },
                {
                    'product': Product.objects.get(id=7),
                    'image': 'product_images/product_7/denji_chainsaw_set_front.jpg'
                },
                {
                    'product': Product.objects.get(id=7),
                    'image': 'product_images/product_7/denji_chainsaw_set_detail.jpg'
                },
                {
                    'product': Product.objects.get(id=8),
                    'image': 'product_images/product_8/power_wig_horns.jpg'
                },
                {
                    'product': Product.objects.get(id=9),
                    'image': 'product_images/product_9/makima_uniform_1.jpg'
                },
                {
                    'product': Product.objects.get(id=9),
                    'image': 'product_images/product_9/makima_uniform_2.webp'
                },
                {
                    'product': Product.objects.get(id=10),
                    'image': 'product_images/product_10/invoker_staff.jpg'
                },
                {
                    'product': Product.objects.get(id=12),
                    'image': 'product_images/product_12/juggernaut_mask_armor.webp'
                },
                {
                    'product': Product.objects.get(id=13),
                    'image': 'product_images/product_13/jon_snow_costume_sword.webp'
                },
                {
                    'product': Product.objects.get(id=14),
                    'image': 'product_images/product_14/daenerys_dress_wig.jpg'
                },
                {
                    'product': Product.objects.get(id=15),
                    'image': 'product_images/product_15/arya_stark_costume.jpg'
                },
                {
                    'product': Product.objects.get(id=16),
                    'image': 'product_images/product_16/cersei_lannister_costume.jpg'
                }
            ]

            for product_image in product_images_data:
                ProductImage.objects.create(**product_image)
            
        self.stdout.write(self.style.SUCCESS('Initialize db command executed successfully'))