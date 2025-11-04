import main, os, csv



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

    # Define duration categories
    def get_duration_category(duration):
        duration = int(duration)
        if duration < 90:
            return "short"
        elif duration <= 120:
            return "medium"
        else:
            return "long"
    
    # Read and organize movies
    movies_by_category = {}
    validation_errors = 0
    
    try:
        with open(path_movies_unscrapped, "r", encoding=encoding, newline="") as movies_unscrapped_file:
            movies_unscrapped_reader = csv.DictReader(movies_unscrapped_file)
            
            for movie in movies_unscrapped_reader:
                # Extract fields
                name = movie[main.HEADER[0]]
                genre = movie[main.HEADER[1]]
                year = movie[main.HEADER[2]]
                duration = movie[main.HEADER[3]]
                rating = movie[main.HEADER[4]]
                director = movie[main.HEADER[5]]
                language = movie[main.HEADER[6]]
                
                # Skip if any essential field is empty
                if not all([name, genre, year, duration, rating, director, language]):
                    continue
                
                # Create fields dictionary for validation
                movie_fields = {
                    main.HEADER[0]: name,
                    main.HEADER[1]: genre,
                    main.HEADER[2]: year,
                    main.HEADER[3]: duration,
                    main.HEADER[4]: rating,
                    main.HEADER[5]: director,
                    main.HEADER[6]: language
                }
                
                # Validate movie fields
                validation_result = validate_movie_fields(movie_fields)
                if validation_result != True:
                    validation_errors += 1
                    continue  # Skip invalid movies
                
                # Get duration category
                duration_cat = get_duration_category(duration)
                
                # Create category key
                category_key = (genre, year, duration_cat)
                
                # Add movie to category
                if category_key not in movies_by_category:
                    movies_by_category[category_key] = []
                
                movies_by_category[category_key].append({
                    main.HEADER[0]: name,
                    main.HEADER[1]: genre,
                    main.HEADER[2]: year,
                    main.HEADER[3]: duration,
                    main.HEADER[4]: rating,
                    main.HEADER[5]: director,
                    main.HEADER[6]: language
                })
    
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
            
            # FIRST: Read existing movies (if file exists)
            existing_movies = []
            if os.path.exists(path_movies):
                with open(path_movies, "r", encoding=encoding, newline="") as existing_file:
                    existing_reader = csv.DictReader(existing_file)
                    existing_movies = list(existing_reader)
            
            # SECOND: Filter duplicates
            unique_movies = []
            for new_movie in movies:
                is_duplicate = False
                
                # Compare with existing movies
                for existing_movie in existing_movies:
                    if movies_are_identical(existing_movie, new_movie):
                        print(f"Duplicate skipped: {new_movie[main.HEADER[0]]}")
                        stats["duplicate_movies_skipped"] += 1
                        is_duplicate = True
                        break
                
                # Compare with other new movies (to avoid duplicates in the same batch)
                if not is_duplicate:
                    for unique_movie in unique_movies:
                        if movies_are_identical(unique_movie, new_movie):
                            print(f"Duplicate in batch skipped: {new_movie[main.HEADER[0]]}")
                            stats["duplicate_movies_skipped"] += 1
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    unique_movies.append(new_movie)
            
            # THIRD: Write all movies (existing + new unique ones)
            all_movies = existing_movies + unique_movies
            
            with open(path_movies, "w", encoding=encoding, newline="") as movies_file:
                movies_writer = csv.DictWriter(movies_file, fieldnames=main.HEADER)
                movies_writer.writeheader()
                movies_writer.writerows(all_movies)
            
            stats["created_files"] += 1
            stats["total_categories"] += 1
            stats["total_movies_processed"] += len(unique_movies)
            
        except Exception as e:
            print(f"Error creating category {folder_path}: {str(e)}")
            continue
    
    return stats



def movies_are_identical(movie1, movie2):
    """
    Compare two movies for exact match in all fields
    """
    return (movie1[main.HEADER[0]] == movie2[main.HEADER[0]] and
            movie1[main.HEADER[1]] == movie2[main.HEADER[1]] and
            str(movie1[main.HEADER[2]]) == str(movie2[main.HEADER[2]]) and
            str(movie1[main.HEADER[3]]) == str(movie2[main.HEADER[3]]) and
            str(movie1[main.HEADER[4]]) == str(movie2[main.HEADER[4]]) and
            movie1[main.HEADER[5]] == movie2[main.HEADER[5]] and
            movie1[main.HEADER[6]] == movie2[main.HEADER[6]])



def validate_existing_movie(path_movies, new_movie, encoding):
    """
    Helper function to validate if a movie already exists
    """
    try:
        if not os.path.exists(path_movies):
            return False
            
        with open(path_movies, "r", encoding=encoding, newline="") as movies_file:
            movies_reader = csv.DictReader(movies_file)
            
            for existing_movie in movies_reader:
                if movies_are_identical(existing_movie, new_movie):
                    return f"Movie {new_movie[main.HEADER[0]]} already exists"
            return False
        
    except Exception as e:
        return f"Error checking movie database: {str(e)}"



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
    
    return True