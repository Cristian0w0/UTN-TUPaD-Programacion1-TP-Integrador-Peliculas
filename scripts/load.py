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



def movies_are_identical(movie1, movie2):
    """
    Compare two movies for exact match in all fields
    """
    def clean_movie(movie):
        return {field: str(movie.get(field, "")).strip() for field in main.HEADER}
    
    movie1_clean = clean_movie(movie1)
    movie2_clean = clean_movie(movie2)
    
    return all(movie1_clean[field] == movie2_clean[field] for field in main.HEADER)



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
        return f"Invalid genre '{fields['genre']}'. Must be one of: {', '.join(sorted(main.GENRES))}"
    
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