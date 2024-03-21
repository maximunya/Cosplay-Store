from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from fandoms.models import Character, Fandom

from .models import Product, Store


@registry.register_document
class ProductDocument(Document):
    id = fields.IntegerField()
    seller = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(analyzer='custom_analyzer',
                                 fields={'exact': fields.KeywordField()}),
        'organization_name': fields.TextField(analyzer='custom_analyzer',
                                              fields={'exact': fields.KeywordField()}),
        'is_verified': fields.BooleanField(),
        'is_admin_store': fields.BooleanField(),
        'bio': fields.TextField(analyzer='custom_analyzer'),
    })
    title = fields.TextField(analyzer='custom_analyzer')
    description = fields.TextField(analyzer='custom_analyzer')
    price = fields.IntegerField(attr='get_real_price')
    discount = fields.IntegerField()
    cosplay_character = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(analyzer='custom_analyzer',
                                 fields={'exact': fields.KeywordField()}),
        'fandom': fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(analyzer='custom_analyzer',
                                     fields={'exact': fields.KeywordField()}),
            'fandom_type': fields.KeywordField()
        }),
    })
    product_type = fields.TextField(analyzer='custom_analyzer',
                                    fields={'exact': fields.KeywordField()})
    size = fields.TextField(analyzer='custom_analyzer',
                            fields={'exact': fields.KeywordField()})
    shoes_size = fields.TextField(analyzer='custom_analyzer',
                                  fields={'exact': fields.KeywordField()})
    timestamp = fields.DateField()
    reviews_count = fields.IntegerField()
    average_score = fields.FloatField()
    total_ordered_quantity = fields.IntegerField()

    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'custom_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'asciifolding',
                                   'stop', 'stemmer',]
                    }
                }
            }
        }

    class Django:
        model = Product
        related_models = [Store, Character, Fandom]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Store):
            return related_instance.store_products.all()
        elif isinstance(related_instance, Character):
            return related_instance.products.all()
        elif isinstance(related_instance, Fandom):
            return Product.objects.filter(cosplay_character__fandom=related_instance)