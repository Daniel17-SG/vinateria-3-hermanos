from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tienda.models import Categoria, Producto

class Command(BaseCommand):
    help = 'Puebla la base de datos con categorías y productos iniciales'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando carga de datos...')

        # 1. Crear Categorías (Agregamos el slug al diccionario defaults)
        cat_tequila, _ = Categoria.objects.get_or_create(
            nombre='Tequila', 
            defaults={'descripcion': 'Tequilas premium y artesanales', 'slug': slugify('Tequila')}
        )
        cat_vodka, _ = Categoria.objects.get_or_create(
            nombre='Vodka', 
            defaults={'descripcion': 'Vodkas destilados importados', 'slug': slugify('Vodka')}
        )
        cat_whisky, _ = Categoria.objects.get_or_create(
            nombre='Whisky', 
            defaults={'descripcion': 'Whiskys escoceses y americanos', 'slug': slugify('Whisky')}
        )

        # 2. Crear Productos
        productos_data = [
            {
                'nombre': 'Tequila Maestro Dobel Diamante',
                'categoria': cat_tequila,
                'precio': 1250.00,
                'stock': 25,
                'descripcion': 'Tequila cristalino reposado, 750ml.',
                'slug': slugify('Tequila Maestro Dobel Diamante')
            },
            {
                'nombre': 'Vodka Absolut',
                'categoria': cat_vodka,
                'precio': 650.00,
                'stock': 40,
                'descripcion': 'Vodka sueco clásico, Destilado 5x, 1 Litro.',
                'slug': slugify('Vodka Absolut')
            },
            {
                'nombre': 'Whisky Buchanan\'s 18',
                'categoria': cat_whisky,
                'precio': 1950.00,
                'stock': 15,
                'descripcion': 'Clásico blend escocés, 18 años.',
                'slug': slugify('Whisky Buchanan\'s 18')
            }
        ]

        for p_data in productos_data:
            nombre_prod = p_data.pop('nombre') # Extraemos el nombre para la búsqueda principal
            Producto.objects.get_or_create(
                nombre=nombre_prod,
                defaults=p_data
            )

        self.stdout.write(self.style.SUCCESS('¡Base de datos poblada con éxito!'))