import os, sys, configparser, unicodedata
#from scripts import filtrar, ordenar, mostrar, cargar, organizar
from scripts import load, organize

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
                show_movies(all_movies)
            case 2:
                show_movie_amount(all_movies)
            case 3:
                show_movie_amount_genre(all_movies)
            case 4:
                show_average_duration(all_movies)
            case 5:
                show_average_duration_genre(all_movies)
            case 6:
                show_sorted_movies(all_movies)
            case 7:
                pass
            case 8:
                pass
            case 9:
                pass
            case 10:
                pass



def show_movies(all_movies):
    if not all_movies:
        print("\nNo hay películas para mostrar")
        return
    print("\n-- Mostrando todas las películas con su ubicación --")
    path_movies_unscrapped = config["Movies"]["Movies_Unscrapped"]
    movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
    print(HEADER)
    for movie in all_movies:
        path_attributes = [
            movies_folder,
            movie["genre"],
            movie["year"],
            get_duration_category(movie["duration"])
        ]
        movie_path = "\\".join(path_attributes)
        print("")
        print(list(movie.values()))
        print(f"Ubicación: {movie_path}")



def show_movie_amount(all_movies):
    if not all_movies:
        print("\nNo hay películas para contar")
        return
    print(f"\n-- Cantidad de películas en total: {len(all_movies)}--")



def show_movie_amount_genre(all_movies):
    if not all_movies:
        print("\nNo hay películas para contar por género")
        return
    genre_amount = {genre: 0 for genre in GENRES}
    for movie in all_movies:
        movie_genre = get_attribute(movie, key=HEADER[1])
        genre_amount[movie_genre] += 1
    print("\n-- Cantidad de películas por género --")
    for genre, amount in genre_amount.items():
        print(f"{genre}: {amount}")



def show_average_duration(all_movies):
    if not all_movies:
        print("\nNo hay películas para promediar duración")
        return
    total_duration = 0
    movie_amount = len(all_movies)
    for movie in all_movies:
        movie_duration = get_attribute(movie, key=HEADER[3])
        total_duration += int(movie_duration)
    average_duration = total_duration / movie_amount
    print(f"\n-- Promedio de duración de todas las películas: {average_duration:.2f} minutos --")



def show_average_duration_genre(all_movies):
    if not all_movies:
        print("\nNo hay películas para promediar duración por género")
        return
    
    genre_duration_amount = {}
    
    for movie in all_movies:
        movie_genre = movie[HEADER[1]]  # género
        movie_duration = movie[HEADER[3]]  # duración
        
        # Convertir duración a entero
        try:
            movie_duration = int(movie_duration)
        except (ValueError, TypeError):
            continue  # Saltar si no se puede convertir a entero
        
        # Inicializar el género si no existe
        if movie_genre not in genre_duration_amount:
            genre_duration_amount[movie_genre] = {
                HEADER[3]: 0,
                "amount": 0
            }
        
        # Acumular duración y contar
        genre_duration_amount[movie_genre][HEADER[3]] += movie_duration
        genre_duration_amount[movie_genre]["amount"] += 1
    
    # Calcular promedios y mostrar resultados
    print("\n--- Promedio de duración de películas por género ---")
    for genre, data in genre_duration_amount.items():
        average_duration = data[HEADER[3]] / data["amount"]
        print(f"{genre}: {average_duration:.2f} minutos")



def show_sorted_movies(all_movies):
    if not all_movies:
        print("\nNo hay películas para ordenar por atributo")
        return
    while True:
        print("\n-- Elegir atributo para ordenar películas --\n"
        "1. Nombre\n"
        "2. Género\n"
        "3. Año de estreno\n"
        "4. Duración en minutos\n"
        "5. Rating\n"
        "6. Director\n"
        "7. Idioma original\n"
        "0. Volver al menú principal")
        opcion = ingresar_opcion(rango_max=7)
        atributo = ""
        match opcion:
            case 1|2|3|4|5|6|7:
                atributo = HEADER[opcion-1]
                break
            case 0:
                return
    sorted_movies = sorted(all_movies, key=lambda x: x[atributo])
    print(f"\n-- Películas ordenadas por {atributo.capitalize()} --")
    print(HEADER)
    for movie in sorted_movies:
        print(list(movie.values()))




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