import os, sys, configparser, unicodedata
#from scripts import filtrar, ordenar, mostrar, cargar, organizar
from scripts import organize, load, show

# Configuración inicial del programa
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8-sig")

# Definición de constantes
HEADER = ["name", "genre", "year", "duration", "rating", "director", "language"]
GENRES = ["Action", "Adventure", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "History", 
        "Horror", "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]
LANGUAGES = ["English", "Spanish", "German", "Italian", "French", 
            "Portuguese", "Russian", "Korean", "Chinese", "Japanese"]

def main():
    # Menú principal del programa
    all_movies = load.get_all_movies()
    while True:
        print("\n--- Menú Principal ---\n"
        "1. Mostrar todas las películas con ruta\n"
        "2. Mostrar cantidad total de películas\n"
        "3. Mostrar cantidad total de películas por género\n"
        "4. Mostrar promedio de duración de todas las películas\n"
        "5. Mostrar promedio de duración de todas las películas por género\n"
        "6. Mostrar películas ordenadas por atributo\n"
        "7. Mostrar películas filtradas por atributo\n"
        "8. Ingresar nueva película\n"
        "9. Actualizar película\n"
        "10. Borrar película\n"
        "0. Salir")
        option = ingresar_opcion(rango_max=10)
        match option:
            case 0:
                print("\nSaliendo...")
                break
            case 1:
                show.show_movies(all_movies)
            case 2:
                show.show_movie_amount(all_movies)
            case 3:
                show.show_movie_amount_genre(all_movies)
            case 4:
                show.show_average_duration(all_movies)
            case 5:
                show.show_average_duration_genre(all_movies)
            case 6:
                show.show_sorted_movies(all_movies)
            case 7:
                show.show_filtered_movies(all_movies)
            case 8:
                all_movies = load.add_new_movie(all_movies)
            case 9:
                all_movies = load.update_movie(all_movies)
            case 10:
                pass





def ingresar_opcion(texto:str = "\nIngresar opción: ", 
                    rango_max:int = sys.maxsize, rango_min:int = 0):
    # Función para validar entrada de opciones del usuario
    try:
        opcion = int(input(texto))
        if (not rango_min <= opcion <= rango_max):
            raise ValueError
    except ValueError:
        print("Opción inválida")
        opcion = None
    finally:
        return opcion



def get_attribute(movie:str|list|dict, index:int=None, key:str=None):
    # Función auxiliar para obtener atributos de una película
    if (isinstance(movie, dict)):
        return movie[key]
    elif (isinstance(movie, list)):
        return movie[index]
    elif (isinstance(movie, str)):
        return movie.strip().split(",")[index]



def remover_tildes(continente:str):
    # Función para normalizar texto removiendo tildes
    return ''.join(
        c for c in unicodedata.normalize('NFD', continente)
        if unicodedata.category(c) != 'Mn'
    )



# Define duration categories
def get_duration_category(duration):
    duration = int(duration)
    if duration < 90:
        return "short"
    elif duration <= 120:
        return "medium"
    else:
        return "long"



if (__name__ == "__main__"):
    # Inicialización del programa - organización de archivos CSV
    rutas_csv = organize.organize_files()
    print("\n" + "="*60)
    print("RUTAS DE ARCHIVOS CSV ORGANIZADOS:")
    print("="*60)
    for nombre, ruta in sorted(rutas_csv.items()):
        print(f"  {nombre:20} -> {ruta}")
    stats = load.categorize_movies()
    print(stats)
    main()