import main, os


def show_movies(all_movies):
    if not all_movies:
        print("\nNo hay películas para mostrar")
        return
    print("\n-- Mostrando todas las películas con su ubicación --")
    path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
    movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
    print(main.HEADER)
    for movie in all_movies:
        path_attributes = [
            movies_folder,
            movie["genre"],
            movie["year"],
            main.get_duration_category(movie["duration"])
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
    genre_amount = {genre: 0 for genre in main.GENRES}
    for movie in all_movies:
        movie_genre = main.get_attribute(movie, key=main.HEADER[1])
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
        movie_duration = main.get_attribute(movie, key=main.HEADER[3])
        total_duration += int(movie_duration)
    average_duration = total_duration / movie_amount
    print(f"\n-- Promedio de duración de todas las películas: {average_duration:.2f} minutos --")



def show_average_duration_genre(all_movies):
    if not all_movies:
        print("\nNo hay películas para promediar duración por género")
        return
    
    genre_duration_amount = {}
    
    for movie in all_movies:
        movie_genre = movie[main.HEADER[1]]  # género
        movie_duration = movie[main.HEADER[3]]  # duración
        
        # Convertir duración a entero
        try:
            movie_duration = int(movie_duration)
        except (ValueError, TypeError):
            continue  # Saltar si no se puede convertir a entero
        
        # Inicializar el género si no existe
        if movie_genre not in genre_duration_amount:
            genre_duration_amount[movie_genre] = {
                main.HEADER[3]: 0,
                "amount": 0
            }
        
        # Acumular duración y contar
        genre_duration_amount[movie_genre][main.HEADER[3]] += movie_duration
        genre_duration_amount[movie_genre]["amount"] += 1
    
    # Calcular promedios y mostrar resultados
    print("\n--- Promedio de duración de películas por género ---")
    for genre, data in genre_duration_amount.items():
        average_duration = data[main.HEADER[3]] / data["amount"]
        print(f"{genre}: {average_duration:.2f} minutos")



def show_sorted_movies(all_movies):
    if not all_movies:
        print("\nNo hay películas para ordenar por atributo")
        return
    atributo = ""
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
        opcion = main.ingresar_opcion(rango_max=7)
        match opcion:
            case 1|2|3|4|5|6|7:
                atributo = main.HEADER[opcion-1]
                break
            case 0:
                return
    sorted_movies = sorted(all_movies, key=lambda x: x[atributo])
    print(f"\n-- Películas ordenadas por {atributo.capitalize()} --")
    print(main.HEADER)
    for movie in sorted_movies:
        print(list(movie.values()))



def show_filtered_movies(all_movies):
    if not all_movies:
        print("\nNo hay películas para filtrar por atributo")
        return
    
    filtered_movies = []
    filter_condition = ""
    atributo = ""
    
    while True:
        print("\n-- Elegir atributo para filtrar películas --\n"
        "1. Género\n"
        "2. Rango de años de estreno\n"
        "3. Rango de duración en minutos\n"
        "4. Rango de rating\n"
        "5. Director\n"
        "6. Idioma original\n"
        "0. Volver al menú principal")
        opcion = main.ingresar_opcion(rango_max=6)
        match opcion:
            case 1|2|3|4|5|6:
                atributo = main.HEADER[opcion]
                break
            case 0:
                return
    
    # Filtro por género
    genre = ""
    if atributo == main.HEADER[1]:  # HEADER[1] es genre
        while True:
            print("\n--- Elegir género para filtrar películas ---")
            for i, genre in enumerate(main.GENRES, 1):
                print(f"{i}. {genre}")
            print("0. Volver al menú principal")
            opcion = main.ingresar_opcion(rango_max=16)
            match opcion:
                case _ if 1 <= opcion <= 16:
                    genre = main.GENRES[opcion-1]
                    break
                case 0:
                    return
        filter_condition = f"{atributo} ({genre})"
        for movie in all_movies:
            if (main.get_attribute(movie, key=atributo) == genre):
                filtered_movies.append(movie)
    
    # Filtro por rango de años
    elif atributo == main.HEADER[2]:  # HEADER[2] es year
        print(f"\n--- Filtrar por rango de {atributo} ---")
        try:
            año_min = int(input("Año mínimo: "))
            año_max = int(input("Año máximo: "))
            
            if año_min > año_max:
                año_min, año_max = año_max, año_min
                
            filter_condition = f"{atributo} ({año_min}-{año_max})"
            for movie in all_movies:
                año_pelicula = int(main.get_attribute(movie, key=atributo))
                if año_min <= año_pelicula <= año_max:
                    filtered_movies.append(movie)
        except ValueError:
            print("Error: Debe ingresar números válidos para los años")
            return
    
    # Filtro por rango de duración
    elif atributo == main.HEADER[3]:  # HEADER[3] es duration
        print(f"\n--- Filtrar por rango de {atributo} (minutos) ---")
        try:
            duracion_min = int(input("Duración mínima (minutos): "))
            duracion_max = int(input("Duración máxima (minutos): "))
            
            if duracion_min > duracion_max:
                duracion_min, duracion_max = duracion_max, duracion_min
                
            filter_condition = f"{atributo} ({duracion_min}-{duracion_max} minutos)"
            for movie in all_movies:
                duracion_pelicula = int(main.get_attribute(movie, key=atributo))
                if duracion_min <= duracion_pelicula <= duracion_max:
                    filtered_movies.append(movie)
        except ValueError:
            print("Error: Debe ingresar números válidos para la duración")
            return
    
    # Filtro por rango de rating
    elif atributo == main.HEADER[4]:  # HEADER[4] es rating
        print(f"\n--- Filtrar por rango de {atributo} (1-10) ---")
        try:
            rating_min = float(input("Rating mínimo (1-10): "))
            rating_max = float(input("Rating máximo (1-10): "))
            
            if rating_min > rating_max:
                rating_min, rating_max = rating_max, rating_min
                
            if rating_min < 0 or rating_max > 10:
                print("Error: El rating debe estar entre 0 y 10")
                return
                
            filter_condition = f"{atributo} ({rating_min}-{rating_max})"
            for movie in all_movies:
                rating_pelicula = float(main.get_attribute(movie, key=atributo))
                if rating_min <= rating_pelicula <= rating_max:
                    filtered_movies.append(movie)
        except ValueError:
            print("Error: Debe ingresar números válidos para el rating")
            return
    
    # Filtro por director
    elif atributo == main.HEADER[5]:  # HEADER[5] es director
        print(f"\n--- Filtrar por {atributo} ---")
        director_buscar = input("Ingrese el nombre del director: ").strip()
        
        if not director_buscar:
            print("Error: Debe ingresar un nombre de director")
            return
            
        filter_condition = f"{atributo} ({director_buscar})"
        for movie in all_movies:
            director_pelicula = main.get_attribute(movie, key=atributo)
            if director_buscar.lower() in director_pelicula.lower():
                filtered_movies.append(movie)
    
    # Filtro por idioma
    elif atributo == main.HEADER[6]:  # HEADER[6] es language
        print(f"\n--- Filtrar por {atributo} ---")
        print("Idiomas disponibles:", ", ".join(sorted(main.LANGUAGES)))
        idioma_buscar = input("Ingrese el idioma: ").strip()
        
        if not idioma_buscar:
            print("Error: Debe ingresar un idioma")
            return
            
        if idioma_buscar not in main.LANGUAGES:
            print(f"Error: El idioma '{idioma_buscar}' no está en la lista de idiomas disponibles")
            return
            
        filter_condition = f"{atributo} ({idioma_buscar})"
        for movie in all_movies:
            idioma_pelicula = main.get_attribute(movie, key=atributo)
            if idioma_pelicula == idioma_buscar:
                filtered_movies.append(movie)
    
    print(f"\n--- Películas filtradas por {filter_condition} ---")
    if not filtered_movies:
        print("No hay películas que cumplan con el filtro")
    else:
        for movie in filtered_movies:
            print(list(movie.values()))