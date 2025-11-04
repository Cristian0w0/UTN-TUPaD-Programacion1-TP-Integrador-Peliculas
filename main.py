import sys, configparser, unicodedata
#from scripts import filtrar, ordenar, mostrar, cargar, organizar
from scripts import load, organize

# Configuración inicial del programa
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8-sig")

# Definición de constantes
HEADER = ["name", "genre", "year", "duration", "rating", "director", "language"]
GENRES = ["Action", "Adventure", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "History", 
        "Horror", "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]

def main():
    # Menú principal del programa
    while True:
        print("\n--- Menú Principal ---\n"
        "1. Filtrar países\n"
        "2. Ordenar países\n"
        "3. Mostrar estadísticas\n"
        "0. Salir")
        opcion = ingresar_opcion(rango_max=3)
        match opcion:
            case 0:
                print("\nSaliendo...")
                break
            case 1:
                menu_filtrar()
            case 2:
                menu_ordenar()
            case 3:
                menu_mostrar()



def menu_filtrar():
    # Menú de filtrado de países
    while True:
        print("\n--- Menú Filtrar ---\n"
        "1. Filtrar países por Continente\n"
        "2. Filtrar países por rango de Población\n"
        "3. Filtrar países por rango de Superficie en Km^2\n"
        "0. Volver al Menú Principal")
        opcion = ingresar_opcion(rango_max=3)
        match opcion:
            case 0:
                break
            case 1:
                filtrar.filtrar_continente()
            case 2:
                filtrar.filtrar_poblacion_o_superficie("Población", 1)
            case 3:
                filtrar.filtrar_poblacion_o_superficie("Superficie en Km^2", 2)



def menu_ordenar():
    # Menú de ordenamiento de países
    while True:
        print("\n--- Menú Ordenar ---\n"
        "1. Ordenar países por Nombre\n"
        "2. Ordenar países por Población\n"
        "3. Ordenar países por Superficie en Km^2\n"
        "0. Volver al menú principal")
        opcion = ingresar_opcion(rango_max=3)
        match opcion:
            case 0:
                break
            case 1:
                ordenar.asc_desc("nombre")
            case 2:
                ordenar.asc_desc("población")
            case 3:
                ordenar.asc_desc("superficie")



def menu_mostrar():
    # Menú de estadísticas y visualización
    while True:
        print("\n--- Menú Estadísticas ---\n"
        "1. Mostrar país(es) con mayor y menor Población\n"
        "2. Mostrar promedio de Población\n"
        "3. Mostrar promedio de Superficie\n"
        "4. Mostrar cantidad de países por Continente\n"
        "5. Mostrar países cargados\n"
        "0. Volver al menú principal")
        opcion = ingresar_opcion(rango_max=5)
        match opcion:
            case 0:
                break
            case 1:
                mostrar.mayor_menor_poblacion()
            case 2:
                mostrar.promedio("Población", 1)
            case 3:
                mostrar.promedio("Superficie en km^2", 2)
            case 4:
                mostrar.paises_por_continente()
            case 5:
                mostrar.mostrar_cargados()



def menu_cargar():
    # Menú de carga y gestión de datos
    while True:
        print("\n--- Menú Cargar ---\n"
        "1. Cargar país por nombre\n"
        "2. Cargar países de continente\n"
        "3. Cargar países reconocidos por la ONU\n"
        "4. Cargar países no reconocidos por la ONU\n"
        "5. Introducir pais manualmente a continente\n"
        "6. Limpiar países cargados\n"
        "7. Limpiar todo y Extraer\n"
        "0. Volver al menú principal")
        opcion = ingresar_opcion(rango_max=7)
        match opcion:
            case 0:
                break
            case 1:
                cargar.cargar_pais(configuracion)
            case 2:
                cargar.cargar_continente(configuracion)
            case 3:
                cargar.cargar_onu(configuracion, "true")
            case 4:
                cargar.cargar_onu(configuracion, "false")
            case 5:
                cargar.introducir_pais(configuracion)
            case 6:
                cargar.limpiar_cargados(configuracion)
            case 7:
                cargar.limpiar_y_extraer(configuracion)



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



def get_atributo(pais:str|list, indice:int):
    # Función auxiliar para obtener atributos de un país
    if (isinstance(pais, list)):
        return pais[indice]
    elif (isinstance(pais, str)):
        return pais.strip().split(",")[indice]


def remover_tildes(continente:str):
    # Función para normalizar texto removiendo tildes
    return ''.join(
        c for c in unicodedata.normalize('NFD', continente)
        if unicodedata.category(c) != 'Mn'
    )


if (__name__ == "__main__"):
    # Inicialización del programa - organización de archivos CSV
    rutas_csv = organize.organize_files()
    print("\n" + "="*60)
    print("RUTAS DE ARCHIVOS CSV ORGANIZADOS:")
    print("="*60)
    for nombre, ruta in sorted(rutas_csv.items()):
        print(f"  {nombre:20} -> {ruta}")
    #main()
    stats = load.categorize_movies()
    print(stats)