import main, os, csv



def get_all_movies() -> list:
    """
    Recursively finds all movies.csv files in the movies folder and subfolders,
    and returns a list with all movies.
    
    Returns:
        list: List with all movies as dictionaries
    """
    path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
    movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
    encoding = main.config["Config"]["Encoding"]
    
    all_movies = []  # Cambiado de dict a list
    
    def find_movies_csv_files(folder_path):
        """
        Recursive function to find all movies.csv files
        """
        try:
            # Check all items in current folder
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if os.path.isdir(item_path):
                    # If it's a directory, search recursively
                    find_movies_csv_files(item_path)
                elif item == "movies.csv":
                    # Found a movies.csv file, read its content
                    try:
                        with open(item_path, "r", encoding=encoding, newline="") as movies_file:
                            movies_reader = csv.DictReader(movies_file)
                            for movie in movies_reader:
                                # Add movie to list as dictionary
                                movie_dict = {field: movie[field] for field in main.HEADER}
                                all_movies.append(movie_dict)

                    except Exception as e:
                        print(f"Error reading {item_path}: {str(e)}")
                        
        except PermissionError:
            print(f"Permission denied accessing folder: {folder_path}")
        except Exception as e:
            print(f"Error accessing folder {folder_path}: {str(e)}")
    
    # Start the recursive search
    find_movies_csv_files(movies_folder)

    return all_movies



def categorize_movies():
    """
    Categorizes movies from a CSV file into a nested folder structure:
    base_dir/genre/year/duration_category/movies.csv
    
    Returns:
        dict: Statistics about the categorization process
    """
    
    path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
    movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
    encoding = main.config["Config"]["Encoding"]
    file_format = main.config["Config"]["File_Format"]
    
    # Read and organize movies
    movies_by_category = {}
    validation_errors = 0
    invalid_movies = []
    processed_movies = []
    
    try:
        with open(path_movies_unscrapped, "r", encoding=encoding, newline="") as movies_unscrapped_file:
            movies_unscrapped_reader = csv.DictReader(movies_unscrapped_file)
            all_movies = list(movies_unscrapped_reader)
            
            for movie in all_movies:
                # Extract fields and clean any None values
                cleaned_movie = {}
                for field in main.HEADER:
                    cleaned_movie[field] = movie.get(field, "") or ""
                
                movie_fields = {field: movie[field] for field in main.HEADER}
                if not all(movie_fields.values()):
                    invalid_movies.append(cleaned_movie)
                    validation_errors += 1
                    continue

                # Validate movie fields
                validation_result = validate_movie_fields(movie_fields)
                if validation_result != True:
                    invalid_movies.append(cleaned_movie)
                    validation_errors += 1
                    continue  # Skip invalid movies
                
                # Get duration category
                duration_cat = main.get_duration_category(movie_fields["duration"])
                
                # Create category key
                category_key = (movie_fields["genre"], movie_fields["year"], duration_cat)
                
                # Add movie to category
                if category_key not in movies_by_category:
                    movies_by_category[category_key] = []
                
                movies_by_category[category_key].append(cleaned_movie)
                processed_movies.append(cleaned_movie)
    
    except FileNotFoundError:
        return {"error": f"CSV file not found: {path_movies_unscrapped}"}
    except Exception as e:
        return {"error": f"Error reading CSV file: {str(e)}"}
    
    # Create folder structure and write CSV files
    stats = {
        "total_categories": 0,
        "total_movies_processed": 0,
        "created_folders": 0,
        "created_files": 0,
        "validation_errors": validation_errors,
        "duplicate_movies_skipped": 0
    }
    
    duplicate_movies = []
    
    for (genre, year, duration_cat), movies in movies_by_category.items():
        # Skip empty categories (shouldn't happen, but just in case)
        if not movies:
            continue
        
        # Create folder path
        folder_path = os.path.join(movies_folder, genre, year, duration_cat)

        try:
            # Create directories if they don't exist
            os.makedirs(folder_path, exist_ok=True)
            stats["created_folders"] += 1
            
            # Create CSV file path
            path_movies = os.path.join(folder_path, "movies." + file_format)
            
            # Read existing movies (if file exists)
            existing_movies = []
            if os.path.exists(path_movies):
                with open(path_movies, "r", encoding=encoding, newline="") as existing_file:
                    existing_reader = csv.DictReader(existing_file)
                    existing_movies = list(existing_reader)
            
            # Filter duplicates
            unique_movies = []
            for new_movie in movies:
                is_duplicate = False
                
                # Compare with existing movies
                for existing_movie in existing_movies:
                    if movies_are_identical(existing_movie, new_movie):
                        print(f"Duplicate skipped: {new_movie[main.HEADER[0]]}")
                        stats["duplicate_movies_skipped"] += 1
                        duplicate_movies.append(new_movie)
                        is_duplicate = True
                        break
                
                # Compare with other new movies (to avoid duplicates in the same batch)
                if not is_duplicate:
                    for unique_movie in unique_movies:
                        if movies_are_identical(unique_movie, new_movie):
                            print(f"Duplicate in batch skipped: {new_movie[main.HEADER[0]]}")
                            stats["duplicate_movies_skipped"] += 1
                            duplicate_movies.append(new_movie)
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    unique_movies.append(new_movie)
            
            # Write all movies (existing + new unique ones)
            all_movies_to_write = existing_movies + unique_movies
            
            # Clean the movies to write (ensure no extra fields)
            cleaned_movies_to_write = []
            for movie in all_movies_to_write:
                cleaned_movie = {}
                for field in main.HEADER:
                    cleaned_movie[field] = movie.get(field, '') or ''
                cleaned_movies_to_write.append(cleaned_movie)
            
            with open(path_movies, "w", encoding=encoding, newline="") as movies_file:
                movies_writer = csv.DictWriter(movies_file, fieldnames=main.HEADER)
                movies_writer.writeheader()
                movies_writer.writerows(cleaned_movies_to_write)
            
            stats["created_files"] += 1
            stats["total_categories"] += 1
            stats["total_movies_processed"] += len(unique_movies)
            
        except Exception as e:
            print(f"Error creating category {folder_path}: {str(e)}")
            continue
    
    # Update the original movies_unscrapped file with only invalid and duplicate movies
    try:
        remaining_movies = invalid_movies + duplicate_movies
        
        # Clean the remaining movies to ensure they only have the fields in main.HEADER
        cleaned_remaining_movies = []
        for movie in remaining_movies:
            cleaned_movie = {}
            for field in main.HEADER:
                cleaned_movie[field] = movie.get(field, '') or ''
            cleaned_remaining_movies.append(cleaned_movie)
        
        with open(path_movies_unscrapped, "w", encoding=encoding, newline="") as movies_unscrapped_file:
            writer = csv.DictWriter(movies_unscrapped_file, fieldnames=main.HEADER)
            writer.writeheader()
            if cleaned_remaining_movies:
                writer.writerows(cleaned_remaining_movies)
        
        print(f"Original file updated. Remaining movies: {len(cleaned_remaining_movies)} (Invalid: {len(invalid_movies)}, Duplicates: {len(duplicate_movies)})")
        
    except Exception as e:
        print(f"Error updating original file: {str(e)}")
        # Print debug information
        print(f"main.HEADER: {main.HEADER}")
        if remaining_movies:
            print(f"First movie keys: {list(remaining_movies[0].keys())}")
    
    return stats



def add_new_movie(all_movies):
    """
    Adds a new movie by user input, validates it, and saves it to the appropriate CSV file.
    
    Args:
        all_movies (list): List of all existing movies as dictionaries
    
    Returns:
        list: Updated list of all movies
    """
    print("\n--- Ingresar nueva pelícuña ---")
    
    # Get movie data from user
    new_movie = {}
    
    # Name
    new_movie[main.HEADER[0]] = input("Nombre de la película: ").strip()
    
    # Genre with menu
    print("\n--- Seleccionar género ---")
    for i, genre in enumerate(main.GENRES, 1):
        print(f"{i}. {genre}")
    while True:
        try:
            genre_choice = int(input("Seleccione el género (número): "))
            if 1 <= genre_choice <= len(main.GENRES):
                new_movie[main.HEADER[1]] = main.GENRES[genre_choice - 1]
                break
            else:
                print(f"Por favor ingrese un número entre 1 y {len(main.GENRES)}")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Year
    while True:
        try:
            year = int(input("Año de estreno: "))
            if year > 0:
                new_movie[main.HEADER[2]] = str(year)
                break
            else:
                print("El año debe ser un número positivo")
        except ValueError:
            print("Por favor ingrese un año válido")
    
    # Duration
    while True:
        try:
            duration = int(input("Duración en minutos: "))
            if duration > 0:
                new_movie[main.HEADER[3]] = str(duration)
                break
            else:
                print("La duración debe ser un número positivo")
        except ValueError:
            print("Por favor ingrese una duración válida")
    
    # Rating
    while True:
        try:
            rating = float(input("Rating (0-10, máximo 1 decimal): "))
            if 0 <= rating <= 10:
                # Check decimal places
                rating_str = str(rating)
                if "." in rating_str:
                    decimal_places = len(rating_str.split(".")[1])
                    if decimal_places > 1:
                        print("El rating puede tener máximo 1 decimal")
                        continue
                new_movie[main.HEADER[4]] = str(rating)
                break
            else:
                print("El rating debe estar entre 0 y 10")
        except ValueError:
            print("Por favor ingrese un rating válido")
    
    # Director
    new_movie[main.HEADER[5]] = input("Director: ").strip()
    
    # Language with menu
    print("\n--- Seleccionar idioma ---")
    for i, language in enumerate(main.LANGUAGES, 1):
        print(f"{i}. {language}")
    while True:
        try:
            lang_choice = int(input("Seleccione el idioma (número): "))
            if 1 <= lang_choice <= len(main.LANGUAGES):
                new_movie[main.HEADER[6]] = main.LANGUAGES[lang_choice - 1]
                break
            else:
                print(f"Por favor ingrese un número entre 1 y {len(main.LANGUAGES)}")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Validate movie fields
    validation_result = validate_movie_fields(new_movie)
    if validation_result != True:
        print(f"\nError de validación: {validation_result}")
        return all_movies
    
    # Check if movie already exists
    for existing_movie in all_movies:
        if movies_are_identical(existing_movie, new_movie):
            print(f"\nLa película '{new_movie[main.HEADER[0]]}' ya existe en la base de datos")
            return all_movies
    
    # Add to the list
    all_movies.append(new_movie)
    print(f"\nPelícula '{new_movie[main.HEADER[0]]}' agregada a la lista")
    
    # Save to CSV file in the appropriate folder structure
    try:
        # Get configuration
        path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
        movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
        encoding = main.config["Config"]["Encoding"]
        file_format = main.config["Config"]["File_Format"]
        
        # Get duration category
        duration_cat = main.get_duration_category(new_movie[main.HEADER[3]])
        
        # Create folder path
        folder_path = os.path.join(movies_folder, new_movie[main.HEADER[1]], new_movie[main.HEADER[2]], duration_cat)
        
        # Create directories if they don't exist
        os.makedirs(folder_path, exist_ok=True)
        
        # Create CSV file path
        csv_path = os.path.join(folder_path, "movies." + file_format)
        
        # Check if file exists to determine if we need to write header
        file_exists = os.path.exists(csv_path)
        
        # Append movie to CSV
        with open(csv_path, "a", encoding=encoding, newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=main.HEADER)
            
            # Write header only if file doesn't exist
            if not file_exists:
                writer.writeheader()
            
            # Write the movie
            writer.writerow(new_movie)
        
        print(f"Película guardada en: {csv_path}")
        
    except Exception as e:
        print(f"Error al guardar la película: {str(e)}")
    
    return all_movies



def update_movie(all_movies):
    """
    Busca películas por criterios y permite modificarlas si se encuentran.
    
    Args:
        all_movies (list): Lista de diccionarios con todas las películas
    
    Returns:
        list: Lista actualizada de películas
    """
    print("\n--- Buscar y modificar película ---")
    
    # Obtener criterios de búsqueda del usuario (todos obligatorios)
    print("Ingrese los criterios de búsqueda (todos son obligatorios):")
    
    name = input("Nombre de la película: ").strip()
    if not name:
        print("El nombre es obligatorio.")
        return all_movies
    
    # Género con menú
    print("\n--- Seleccionar género ---")
    for i, genre in enumerate(main.GENRES, 1):
        print(f"{i}. {genre}")
    while True:
        try:
            genre_choice = int(input("Seleccione el género (número): "))
            if 1 <= genre_choice <= len(main.GENRES):
                genre = main.GENRES[genre_choice - 1]
                break
            else:
                print(f"Por favor ingrese un número entre 1 y {len(main.GENRES)}")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Año
    while True:
        year = input("Año de lanzamiento: ").strip()
        if year:
            try:
                year_int = int(year)
                if year_int > 0:
                    break
                else:
                    print("El año debe ser un número positivo")
            except ValueError:
                print("Por favor ingrese un año válido")
        else:
            print("El año es obligatorio")
    
    # Categoría de duración con menú - USANDO LAS MISMAS CATEGORÍAS QUE get_duration_category()
    print("\n--- Seleccionar categoría de duración ---")
    duration_categories = ["short", "medium", "long"]  # Consistentes con get_duration_category()
    duration_category_names = {"short": "Corta", "medium": "Media", "long": "Larga"}  # Para mostrar nombres en español
    
    for i, cat in enumerate(duration_categories, 1):
        print(f"{i}. {duration_category_names[cat]}")
    
    while True:
        try:
            duration_choice = int(input("Seleccione la categoría de duración (número): "))
            if 1 <= duration_choice <= len(duration_categories):
                duration_cat = duration_categories[duration_choice - 1]
                break
            else:
                print(f"Por favor ingrese un número entre 1 y {len(duration_categories)}")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Buscar películas que coincidan con los criterios
    matching_movies = []
    
    for movie in all_movies:
        matches = True
        
        # Verificar nombre
        if name != movie[main.HEADER[0]]:
            matches = False
        
        # Verificar género
        if genre != movie[main.HEADER[1]]:
            matches = False
        
        # Verificar año
        if year != movie[main.HEADER[2]]:
            matches = False
        
        # Verificar categoría de duración usando get_duration_category()
        movie_duration = int(movie[main.HEADER[3]])
        movie_duration_cat = main.get_duration_category(movie_duration)
        
        if duration_cat != movie_duration_cat:
            matches = False

        if matches:
            matching_movies.append(movie)
    
    # Mostrar resultados
    if not matching_movies:
        print(f"\nNo se encontraron películas que coincidan con todos los criterios especificados:")
        print(f"Nombre: {name}")
        print(f"Género: {genre}")
        print(f"Año: {year}")
        print(f"Categoría de duración: {duration_category_names[duration_cat]}")
        return all_movies
    
    print(f"\nSe encontraron {len(matching_movies)} película(s) que coinciden:")
    for i, movie in enumerate(matching_movies, 1):
        actual_duration_cat = main.get_duration_category(int(movie[main.HEADER[3]]))
        print(f"{i}. {movie[main.HEADER[0]]} ({movie[main.HEADER[2]]}) - {movie[main.HEADER[1]]} - {duration_category_names[actual_duration_cat]} - Rating: {movie[main.HEADER[4]]}")
    
    # Si hay múltiples resultados, dejar que el usuario elija cuál modificar
    if len(matching_movies) > 1:
        while True:
            try:
                choice = int(input(f"\nSeleccione la película a modificar (1-{len(matching_movies)}): "))
                if 1 <= choice <= len(matching_movies):
                    movie_to_modify = matching_movies[choice - 1]
                    break
                else:
                    print(f"Por favor ingrese un número entre 1 y {len(matching_movies)}")
            except ValueError:
                print("Por favor ingrese un número válido")
    else:
        movie_to_modify = matching_movies[0]
    
    # Mostrar menú de atributos a modificar
    print(f"\n--- Modificando: {movie_to_modify[main.HEADER[0]]} ---")
    print("Seleccione el atributo a modificar:")
    attribute_names = {
        "0": "Nombre",
        "1": "Género", 
        "2": "Año",
        "3": "Duración",
        "4": "Rating",
        "5": "Director",
        "6": "Idioma"
    }
    
    for key, value in attribute_names.items():
        print(f"{key}. {value}")
    
    while True:
        attribute_choice = input("\nSeleccione el atributo (número): ").strip()
        if attribute_choice in attribute_names:
            break
        else:
            print("Por favor seleccione un número válido del menú")
    
    # Obtener nuevo valor según el atributo seleccionado
    attribute_index = int(attribute_choice)
    attribute_name = main.HEADER[attribute_index]
    current_value = movie_to_modify[attribute_name]
    
    print(f"\nAtributo seleccionado: {attribute_names[attribute_choice]}")
    print(f"Valor actual: {current_value}")
    
    new_value = None
    
    if attribute_choice == "0":  # Nombre
        while True:
            new_value = input("Nuevo nombre: ").strip()
            if new_value:
                break
            else:
                print("El nombre no puede estar vacío")
    
    elif attribute_choice == "1":  # Género
        print("\n--- Seleccionar nuevo género ---")
        for i, genre_option in enumerate(main.GENRES, 1):
            print(f"{i}. {genre_option}")
        while True:
            try:
                genre_choice = int(input("Seleccione el nuevo género (número): "))
                if 1 <= genre_choice <= len(main.GENRES):
                    new_value = main.GENRES[genre_choice - 1]
                    break
                else:
                    print(f"Por favor ingrese un número entre 1 y {len(main.GENRES)}")
            except ValueError:
                print("Por favor ingrese un número válido")
    
    elif attribute_choice == "2":  # Año
        while True:
            try:
                year = int(input("Nuevo año de estreno: "))
                if year > 0:
                    new_value = str(year)
                    break
                else:
                    print("El año debe ser un número positivo")
            except ValueError:
                print("Por favor ingrese un año válido")
    
    elif attribute_choice == "3":  # Duración
        while True:
            try:
                duration = int(input("Nueva duración en minutos: "))
                if duration > 0:
                    new_value = str(duration)
                    break
                else:
                    print("La duración debe ser un número positivo")
            except ValueError:
                print("Por favor ingrese una duración válida")
    
    elif attribute_choice == "4":  # Rating
        while True:
            try:
                rating = float(input("Nuevo rating (0-10, máximo 1 decimal): "))
                if 0 <= rating <= 10:
                    rating_str = str(rating)
                    if "." in rating_str:
                        decimal_places = len(rating_str.split(".")[1])
                        if decimal_places > 1:
                            print("El rating puede tener máximo 1 decimal")
                            continue
                    new_value = str(rating)
                    break
                else:
                    print("El rating debe estar entre 0 y 10")
            except ValueError:
                print("Por favor ingrese un rating válido")
    
    elif attribute_choice == "5":  # Director
        while True:
            new_value = input("Nuevo director: ").strip()
            if new_value:
                break
            else:
                print("El director no puede estar vacío")
    
    elif attribute_choice == "6":  # Idioma
        print("\n--- Seleccionar nuevo idioma ---")
        for i, language in enumerate(main.LANGUAGES, 1):
            print(f"{i}. {language}")
        while True:
            try:
                lang_choice = int(input("Seleccione el nuevo idioma (número): "))
                if 1 <= lang_choice <= len(main.LANGUAGES):
                    new_value = main.LANGUAGES[lang_choice - 1]
                    break
                else:
                    print(f"Por favor ingrese un número entre 1 y {len(main.LANGUAGES)}")
            except ValueError:
                print("Por favor ingrese un número válido")
    
    # Actualizar el valor en la lista en memoria
    movie_to_modify[attribute_name] = new_value
    
    # Si se modificó la duración, necesitamos mover el archivo a la categoría correcta
    if attribute_choice == "3":  # Si se modificó la duración
        old_duration_cat = main.get_duration_category(int(current_value))
        new_duration_cat = main.get_duration_category(int(new_value))
        
        # Si cambió la categoría de duración, mover el archivo
        if old_duration_cat != new_duration_cat:
            move_movie_to_correct_category(movie_to_modify, old_duration_cat, new_duration_cat)
    
    # Actualizar el archivo CSV correspondiente
    try:
        # Obtener configuración
        path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
        movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
        encoding = main.config["Config"]["Encoding"]
        file_format = main.config["Config"]["File_Format"]
        
        # Encontrar y actualizar todos los archivos CSV que contengan esta película
        updated = False
        
        def update_movie_in_csv_files(folder_path):
            nonlocal updated
            try:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    
                    if os.path.isdir(item_path):
                        update_movie_in_csv_files(item_path)
                    elif item == "movies." + file_format:
                        # Leer el archivo CSV
                        movies_in_file = []
                        with open(item_path, "r", encoding=encoding, newline="") as csv_file:
                            reader = csv.DictReader(csv_file)
                            movies_in_file = list(reader)
                        
                        # Buscar y actualizar la película
                        file_modified = False
                        for i, movie_in_file in enumerate(movies_in_file):
                            if movies_are_identical(movie_in_file, movie_to_modify):
                                # Actualizar el atributo específico
                                movies_in_file[i][attribute_name] = new_value
                                file_modified = True
                                updated = True
                                break
                        
                        # Si se modificó, reescribir el archivo
                        if file_modified:
                            with open(item_path, "w", encoding=encoding, newline="") as csv_file:
                                writer = csv.DictWriter(csv_file, fieldnames=main.HEADER)
                                writer.writeheader()
                                writer.writerows(movies_in_file)
                            print(f"Película actualizada en: {item_path}")
                            
            except Exception as e:
                print(f"Error accediendo a {folder_path}: {str(e)}")
        
        # Iniciar la búsqueda recursiva
        update_movie_in_csv_files(movies_folder)
        
        if not updated:
            print("Advertencia: No se pudo encontrar la película en los archivos CSV para actualizar.")
        else:
            print(f"\n¡Película actualizada exitosamente!")
            print(f"'{attribute_names[attribute_choice]}' cambiado de '{current_value}' a '{new_value}'")
            
    except Exception as e:
        print(f"Error al actualizar el archivo CSV: {str(e)}")
    
    return all_movies


def move_movie_to_correct_category(movie, old_duration_cat, new_duration_cat):
    """
    Mueve una película a la categoría de duración correcta si cambió su duración.
    """
    try:
        path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
        movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
        encoding = main.config["Config"]["Encoding"]
        file_format = main.config["Config"]["File_Format"]
        
        # Ruta antigua
        old_folder = os.path.join(movies_folder, movie[main.HEADER[1]], movie[main.HEADER[2]], old_duration_cat)
        old_file = os.path.join(old_folder, "movies." + file_format)
        
        # Ruta nueva
        new_folder = os.path.join(movies_folder, movie[main.HEADER[1]], movie[main.HEADER[2]], new_duration_cat)
        new_file = os.path.join(new_folder, "movies." + file_format)
        
        # Crear nueva carpeta si no existe
        os.makedirs(new_folder, exist_ok=True)
        
        # Remover de archivo antiguo
        if os.path.exists(old_file):
            with open(old_file, "r", encoding=encoding, newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                movies = list(reader)
            
            # Filtrar la película a mover
            updated_movies = [m for m in movies if not movies_are_identical(m, movie)]
            
            # Reescribir archivo antiguo sin la película
            with open(old_file, "w", encoding=encoding, newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=main.HEADER)
                writer.writeheader()
                writer.writerows(updated_movies)
        
        # Agregar a nuevo archivo
        movies_in_new = []
        if os.path.exists(new_file):
            with open(new_file, "r", encoding=encoding, newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                movies_in_new = list(reader)
        
        # Agregar la película actualizada
        movies_in_new.append(movie)
        
        with open(new_file, "w", encoding=encoding, newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=main.HEADER)
            writer.writeheader()
            writer.writerows(movies_in_new)
        
        print(f"Película movida de categoría: {old_duration_cat} -> {new_duration_cat}")
        
    except Exception as e:
        print(f"Error moviendo película a nueva categoría: {str(e)}")



def movies_are_identical(movie1, movie2):
    """
    Compare two movies for exact match in all fields
    """
    def clean_movie(movie):
        return {field: str(movie.get(field, "")).strip() for field in main.HEADER}
    
    movie1_clean = clean_movie(movie1)
    movie2_clean = clean_movie(movie2)
    
    return all(movie1_clean[field] == movie2_clean[field] for field in main.HEADER)



def validate_movie_fields(fields):
    """
    Validates movie fields according to specified rules.
    
    Args:
        fields (dict): Dictionary containing movie fields with keys:
                    "name", "genre", "year", "duration", "rating", "director", "language"
    
    Returns:
        bool|str: True if all fields are valid, otherwise a string describing the error
    """
    
    # Check for empty fields
    for field_name, field_value in fields.items():
        if not field_value and field_value != 0:  # Allow 0 as valid value
            return f"Field '{field_name}' cannot be empty"
    
    # Validate genre
    if fields["genre"] not in main.GENRES:
        return f"Invalid genre '{fields["genre"]}'. Must be one of: {", ".join(sorted(main.GENRES))}"
    
    # Validate year - positive integer
    try:
        year = int(fields["year"])
        if year <= 0:
            return "Year must be a positive integer"
    except (ValueError, TypeError):
        return "Year must be a valid integer"
    
    # Validate duration - positive integer
    try:
        duration = int(fields["duration"])
        if duration <= 0:
            return "Duration must be a positive integer"
    except (ValueError, TypeError):
        return "Duration must be a valid integer"
    
    # Validate rating - float with max 1 decimal
    try:
        rating = float(fields["rating"])
        if rating < 0:
            return "Rating cannot be negative"
        
        # Check decimal places
        rating_str = str(fields["rating"])
        if "." in rating_str:
            decimal_places = len(rating_str.split(".")[1])
            if decimal_places > 1:
                return "Rating can have maximum 1 decimal place"
    except (ValueError, TypeError):
        return "Rating must be a valid number"
    
    # Validate language - must be in available languages
    if fields["language"] not in main.LANGUAGES:
        return f"Invalid language '{fields["language"]}'. Must be one of: {", ".join(sorted(main.LANGUAGES))}"
    
    return True