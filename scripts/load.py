import main, os, csv



def get_config():
    """Get commonly used configuration values"""
    path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
    movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
    encoding = main.config["Config"]["Encoding"]
    file_format = main.config["Config"]["File_Format"]
    return movies_folder, encoding, file_format, path_movies_unscrapped



def clean_movie_data(movie):
    """Clean movie data to ensure only main.HEADER fields are present"""
    return {field: str(movie.get(field, "")).strip() for field in main.HEADER}



def get_movie_file_path(genre, year, duration, file_format):
    """Get the file path for a movie based on its category"""
    movies_folder, _, _, _ = get_config()
    duration_category = main.get_duration_category(duration)
    folder_path = os.path.join(movies_folder, genre, year, duration_category)
    return os.path.join(folder_path, f"movies.{file_format}"), folder_path



def read_csv_file(file_path, encoding):
    """Read a CSV file and return its content as list of dictionaries"""
    try:
        with open(file_path, "r", encoding=encoding, newline="") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return []



def write_csv_file(file_path, data, encoding, fieldnames):
    """Write data to a CSV file"""
    try:
        with open(file_path, "w", encoding=encoding, newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            if data:
                writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {str(e)}")
        return False



def append_to_csv_file(file_path, row, encoding, fieldnames):
    """Append a row to a CSV file, creating header if file doesn't exist"""
    file_exists = os.path.exists(file_path)
    try:
        with open(file_path, "a", encoding=encoding, newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error appending to {file_path}: {str(e)}")
        return False



def get_validated_input(prompt, input_type=int, validation_func=None, error_msg="Invalid input"):
    """Get and validate user input with retry logic"""
    while True:
        try:
            value = input_type(input(prompt))
            if validation_func and not validation_func(value):
                print(error_msg)
                continue
            return value
        except ValueError:
            print("Please enter a valid value")



def select_from_menu(options, prompt="Select an option (number): "):
    """Display a menu and get user selection"""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        choice = main.insert_option(prompt, len(options), 1)
        if choice is not None:
            return options[choice - 1]
        print("Please enter a valid number")



def get_movie_search_criteria():
    """Get movie search criteria from user"""
    print("\nEnter search criteria:")
    name = input("Movie name: ").strip()
    
    print("\n--- Select Genre ---")
    genre = select_from_menu(main.GENRES, "Select genre (number): ")
    
    # Get and validate year input
    year = get_validated_input(
        "Release year: ", 
        int, 
        lambda x: x > 0, 
        "Year must be a positive number"
    )
    
    # Get and validate duration input
    duration = get_validated_input(
        "Duration in minutes: ", 
        int, 
        lambda x: x > 0, 
        "Duration must be a positive number"
    )
    
    duration_category = main.get_duration_category(duration)
    
    return name, genre, str(year), duration_category



def get_movie_attribute_input(attribute, current_value=None):
    """Get input for a specific movie attribute"""
    if attribute == "genre":
        print("\n--- Select Genre ---")
        return select_from_menu(main.GENRES, "Select genre (number): ")
    
    elif attribute == "year":
        return str(get_validated_input(
            "Release year: " if not current_value else f"New release year (current: {current_value}): ",
            int,
            lambda x: x > 0,
            "Year must be a positive number"
        ))
    
    elif attribute == "duration":
        return str(get_validated_input(
            "Duration in minutes: " if not current_value else f"New duration in minutes (current: {current_value}): ",
            int,
            lambda x: x > 0,
            "Duration must be a positive number"
        ))
    
    elif attribute == "rating":
        def validate_rating(r):
            if not (0 <= r <= 10):
                return False
            rating_str = str(r)
            if "." in rating_str:
                return len(rating_str.split(".")[1]) <= 1
            return True
        
        return str(get_validated_input(
            "Rating (0-10, maximum 1 decimal): " if not current_value else f"New rating (0-10, current: {current_value}): ",
            float,
            validate_rating,
            "Rating must be between 0 and 10 with max 1 decimal"
        ))
    
    elif attribute == "language":
        print("\n--- Select Language ---")
        return select_from_menu(main.LANGUAGES, "Select language (number): ")
    
    else:  # name or director (free text fields)
        prompt = f"Enter {attribute}: " if not current_value else f"New {attribute} (current: {current_value}): "
        return input(prompt).strip()



def find_movie_by_criteria(all_movies, name, genre, year, duration_category):
    """Find a movie that matches all search criteria"""
    for movie in all_movies:
        if (movie["name"].strip().lower() == name.lower() and
            movie["genre"] == genre and
            movie["year"] == year and
            main.get_duration_category(movie["duration"]) == duration_category):
            return movie
    return None



def movies_are_identical(movie1, movie2):
    """Compare two movies for exact match in all fields"""
    movie1_clean = clean_movie_data(movie1)
    movie2_clean = clean_movie_data(movie2)
    return all(movie1_clean[field] == movie2_clean[field] for field in main.HEADER)



def validate_movie_fields(fields):
    """Validates movie fields according to specified rules"""
    # Check for empty fields
    for field_name, field_value in fields.items():
        if not field_value and field_value != 0:
            return f"Field '{field_name}' cannot be empty"
    
    # Validate genre - must be in predefined list
    if fields["genre"] not in main.GENRES:
        return f"Invalid genre '{fields['genre']}'. Must be one of: {', '.join(sorted(main.GENRES))}"
    
    # Validate year - must be positive integer
    try:
        year = int(fields["year"])
        if year <= 0:
            return "Year must be a positive integer"
    except (ValueError, TypeError):
        return "Year must be a valid integer"
    
    # Validate duration - must be positive integer
    try:
        duration = int(fields["duration"])
        if duration <= 0:
            return "Duration must be a positive integer"
    except (ValueError, TypeError):
        return "Duration must be a valid integer"
    
    # Validate rating - must be between 0-10 with max 1 decimal
    try:
        rating = float(fields["rating"])
        if rating < 0:
            return "Rating cannot be negative"
        rating_str = str(fields["rating"])
        if "." in rating_str and len(rating_str.split(".")[1]) > 1:
            return "Rating can have maximum 1 decimal place"
    except (ValueError, TypeError):
        return "Rating must be a valid number"
    
    # Validate language - must be in predefined list
    if fields["language"] not in main.LANGUAGES:
        return f"Invalid language '{fields['language']}'. Must be one of: {', '.join(sorted(main.LANGUAGES))}"
    
    return True



def clean_empty_files_and_folders(movies_folder):
    """Remove empty CSV files and folders recursively, including year and genre folders"""
    empty_files = []
    empty_folders = []
    
    def find_empty_items(folder_path):
        # Process subfolders first (depth-first)
        items_processed = False
        for item in os.listdir(folder_path):
            items_processed = True
            item_path = os.path.join(folder_path, item)
            
            if os.path.isdir(item_path):
                find_empty_items(item_path)  # Recursively check subfolders
                # After processing subfolders, check if this folder is now empty
                if len(os.listdir(item_path)) == 0:
                    empty_folders.append(item_path)
            elif item.endswith(".csv"):
                try:
                    with open(item_path, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        # Check if file has only header or is empty
                        rows = list(reader)
                        if len(rows) <= 1:  # Only header or empty
                            empty_files.append(item_path)
                except Exception as e:
                    print(f"Error reading file {item_path}: {str(e)}")
        
        # If no items were processed (empty folder), add it to empty folders
        if not items_processed and len(os.listdir(folder_path)) == 0:
            empty_folders.append(folder_path)
    
    # Start the search
    find_empty_items(movies_folder)
    
    # Remove empty files
    for file_path in empty_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed empty file: {file_path}")
        except Exception as e:
            print(f"Error removing file {file_path}: {str(e)}")
    
    # Remove empty folders (from deepest to shallowest)
    # Sort by path length to ensure deepest folders are removed first
    empty_folders.sort(key=lambda x: len(x.split(os.sep)), reverse=True)
    
    removed_folders = set()
    
    for folder_path in empty_folders:
        try:
            if (os.path.exists(folder_path) and 
                os.path.isdir(folder_path) and 
                len(os.listdir(folder_path)) == 0 and
                folder_path != movies_folder):  # Don't remove the main movies folder
                
                os.rmdir(folder_path)
                removed_folders.add(folder_path)
                print(f"Removed empty folder: {folder_path}")
                
        except Exception as e:
            print(f"Error removing folder {folder_path}: {str(e)}")
    
    # After removing folders, check if parent folders became empty and remove them too
    # This handles the case where we remove a duration folder and the year folder becomes empty
    for folder_path in removed_folders:
        parent_folder = os.path.dirname(folder_path)
        while (parent_folder != movies_folder and 
            os.path.exists(parent_folder) and 
            os.path.isdir(parent_folder) and 
            len(os.listdir(parent_folder)) == 0):
            
            try:
                os.rmdir(parent_folder)
                print(f"Removed empty parent folder: {parent_folder}")
                removed_folders.add(parent_folder)
                parent_folder = os.path.dirname(parent_folder)  # Move up one level
            except Exception as e:
                print(f"Error removing parent folder {parent_folder}: {str(e)}")
                break
    
    return len(empty_files) + len(removed_folders)  # Return count of items cleaned



def get_all_movies() -> list:
    """Recursively finds all movies.csv files and returns a list with all movies"""
    movies_folder, encoding, _, _ = get_config()
    all_movies = []
    
    def find_movies_csv_files(folder_path):
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if os.path.isdir(item_path):
                    find_movies_csv_files(item_path)
                elif item == "movies.csv":
                    # Read movies from CSV file and add to list
                    movies_data = read_csv_file(item_path, encoding)
                    for movie in movies_data:
                        movie_dict = clean_movie_data(movie)
                        all_movies.append(movie_dict)
        except PermissionError:
            print(f"Permission denied accessing folder: {folder_path}")
        except Exception as e:
            print(f"Error accessing folder {folder_path}: {str(e)}")
    
    find_movies_csv_files(movies_folder)
    return all_movies



def categorize_movies():
    """Categorizes movies into genre/year/duration_category folder structure"""
    movies_folder, encoding, file_format, path_movies_unscrapped = get_config()
    
    # Read and organize movies
    movies_by_category = {}
    validation_errors = 0
    invalid_movies = []
    
    try:
        all_movies = read_csv_file(path_movies_unscrapped, encoding)
        
        for movie in all_movies:
            cleaned_movie = clean_movie_data(movie)
            
            # Check for empty fields
            if not all(cleaned_movie.values()):
                invalid_movies.append(cleaned_movie)
                validation_errors += 1
                continue

            # Validate movie
            validation_result = validate_movie_fields(cleaned_movie)
            if validation_result != True:
                invalid_movies.append(cleaned_movie)
                validation_errors += 1
                continue
            
            # Categorize movie by genre, year, and duration
            duration_cat = main.get_duration_category(cleaned_movie["duration"])
            category_key = (cleaned_movie["genre"], cleaned_movie["year"], duration_cat)
            
            if category_key not in movies_by_category:
                movies_by_category[category_key] = []
            movies_by_category[category_key].append(cleaned_movie)
    
    except FileNotFoundError:
        return {"error": f"CSV file not found: {path_movies_unscrapped}"}
    except Exception as e:
        return {"error": f"Error reading CSV file: {str(e)}"}
    
    # Process categories and create folder structure
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
        if not movies:
            continue
        
        file_path, folder_path = get_movie_file_path(genre, year, movies[0]["duration"], file_format)
        
        try:
            # Create directory structure
            os.makedirs(folder_path, exist_ok=True)
            stats["created_folders"] += 1
            
            # Read existing movies (if file exists)
            existing_movies = read_csv_file(file_path, encoding) if os.path.exists(file_path) else []
            
            # Filter duplicates
            unique_movies = []
            for new_movie in movies:
                is_duplicate = any(movies_are_identical(existing_movie, new_movie) for existing_movie in existing_movies)
                is_duplicate = is_duplicate or any(movies_are_identical(unique_movie, new_movie) for unique_movie in unique_movies)
                
                if is_duplicate:
                    print(f"Duplicate skipped: {new_movie[main.HEADER[0]]}")
                    stats["duplicate_movies_skipped"] += 1
                    duplicate_movies.append(new_movie)
                else:
                    unique_movies.append(new_movie)
            
            # Write all movies to CSV file
            all_movies_to_write = existing_movies + unique_movies
            cleaned_movies = [clean_movie_data(movie) for movie in all_movies_to_write]
            
            if write_csv_file(file_path, cleaned_movies, encoding, main.HEADER):
                stats["created_files"] += 1
                stats["total_categories"] += 1
                stats["total_movies_processed"] += len(unique_movies)
            
        except Exception as e:
            print(f"Error creating category {folder_path}: {str(e)}")
            continue
    
    # Update original file with remaining movies (invalid and duplicates)
    remaining_movies = invalid_movies + duplicate_movies
    cleaned_remaining = [clean_movie_data(movie) for movie in remaining_movies]
    
    if write_csv_file(path_movies_unscrapped, cleaned_remaining, encoding, main.HEADER):
        print(f"Original file updated. Remaining movies: {len(cleaned_remaining)}")
    
    return stats



def add_new_movie(all_movies):
    """Adds a new movie by user input and saves it to the appropriate CSV file"""
    print("\n--- Add New Movie ---")
    
    new_movie = {}
    # Get movie data for each field
    for i, field in enumerate(main.HEADER):
        if field == "genre":
            new_movie[field] = select_from_menu(main.GENRES, "Select genre (number): ")
        elif field == "language":
            new_movie[field] = select_from_menu(main.LANGUAGES, "Select language (number): ")
        elif field in ["year", "duration"]:
            new_movie[field] = str(get_validated_input(
                f"{field.capitalize()}: ", 
                int, 
                lambda x: x > 0, 
                f"{field.capitalize()} must be positive"
            ))
        elif field == "rating":
            new_movie[field] = get_movie_attribute_input("rating")
        else:
            new_movie[field] = input(f"{field.capitalize()}: ").strip()
    
    # Validate movie
    validation_result = validate_movie_fields(new_movie)
    if validation_result != True:
        print(f"\nValidation error: {validation_result}")
        return all_movies
    
    # Check for duplicates
    if any(movies_are_identical(existing_movie, new_movie) for existing_movie in all_movies):
        print(f"\nMovie '{new_movie['name']}' already exists in the database")
        return all_movies
    
    # Add to list and save to file
    all_movies.append(new_movie)
    print(f"\nMovie '{new_movie['name']}' added to the list")
    
    # Save to CSV in appropriate folder
    movies_folder, encoding, file_format, _ = get_config()
    file_path, folder_path = get_movie_file_path(
        new_movie["genre"], 
        new_movie["year"], 
        new_movie["duration"], 
        file_format
    )
    
    os.makedirs(folder_path, exist_ok=True)
    if append_to_csv_file(file_path, new_movie, encoding, main.HEADER):
        print(f"Movie saved to: {file_path}")
    
    return all_movies



def update_movie(all_movies):
    """Searches for a movie and allows modifying one of its attributes"""
    print("\n--- Update Existing Movie ---")
    
    # Get search criteria
    name, genre, year, duration_category = get_movie_search_criteria()
    
    # Find movie
    found_movie = find_movie_by_criteria(all_movies, name, genre, year, duration_category)
    if not found_movie:
        print("\nNo movie found that matches all the specified criteria.")
        return all_movies
    
    print(f"\nMovie found!: {found_movie['name']}")
    print("Current movie data:")
    for field in main.HEADER:
        print(f"  {field}: {found_movie[field]}")
    
    # Select attribute to modify
    print("\n--- Attributes Available for Modification ---")
    attribute = select_from_menu(main.HEADER, "Select attribute to modify (number): ")
    
    # Get new value
    new_value = get_movie_attribute_input(attribute, found_movie[attribute])
    
    # Store original values and validate
    original_movie = found_movie.copy()
    test_movie = found_movie.copy()
    test_movie[attribute] = new_value
    
    validation_result = validate_movie_fields(test_movie)
    if validation_result != True:
        print(f"\nValidation error: {validation_result}")
        return all_movies
    
    # Update in memory
    previous_value = found_movie[attribute]
    found_movie[attribute] = new_value
    
    print(f"\nAttribute '{attribute}' modified:")
    print(f"  Previous value: {previous_value}")
    print(f"  New value: {new_value}")
    
    # Update files
    movies_folder, encoding, file_format, _ = get_config()
    
    try:
        # Calculate new path (in case category changed)
        new_file_path, new_folder_path = get_movie_file_path(
            found_movie["genre"], 
            found_movie["year"], 
            found_movie["duration"], 
            file_format
        )
        
        os.makedirs(new_folder_path, exist_ok=True)
        
        # First: Collect all files that need to be updated
        files_to_process = []
        
        def collect_csv_files(folder_path):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    collect_csv_files(item_path)
                elif item.endswith(f".{file_format}"):
                    files_to_process.append(item_path)
        
        collect_csv_files(movies_folder)
        
        # Second: Process each file (no recursion during modification)
        for file_path in files_to_process:
            try:
                movies_data = read_csv_file(file_path, encoding)
                if not movies_data:
                    continue
                
                updated_movies = []
                movie_found = False
                
                for movie in movies_data:
                    if movies_are_identical(movie, original_movie):
                        movie_found = True
                        if file_path == new_file_path:
                            updated_movies.append(found_movie.copy())
                            print(f"Movie updated in: {file_path}")
                        else:
                            print(f"Movie removed from: {file_path}")
                    else:
                        updated_movies.append(movie)
                
                # Add to target file if not found
                if not movie_found and file_path == new_file_path:
                    updated_movies.append(found_movie.copy())
                    print(f"Movie added to: {file_path}")
                
                # Write the file only if there are movies
                if updated_movies:
                    write_csv_file(file_path, updated_movies, encoding, main.HEADER)
                else:
                    # File is now empty, remove it
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Empty file removed: {file_path}")
                        
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
        
        # Create target file if it doesn't exist
        if not os.path.exists(new_file_path):
            write_csv_file(new_file_path, [found_movie], encoding, main.HEADER)
            print(f"New file created with updated movie: {new_file_path}")
        
        # Use a safer cleanup function that doesn't modify during iteration
        print("\nCleaning up empty files and folders...")
        items_cleaned = safe_clean_empty_files_and_folders(movies_folder)
        if items_cleaned > 0:
            print(f"Cleaned up {items_cleaned} empty items")
        else:
            print("No empty items found to clean")
        
        print("Movie successfully updated in all files!")
        
    except Exception as e:
        print(f"Error updating files: {str(e)}")
        found_movie[attribute] = previous_value
        print("Changes reverted in memory due to file update error.")

    return all_movies



def safe_clean_empty_files_and_folders(movies_folder):
    """Safer version that collects all items first before deleting, including parent folders"""
    empty_files = []
    empty_folders = []
    
    # First pass: collect all empty items without modifying
    def collect_empty_items(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            if os.path.isdir(item_path):
                collect_empty_items(item_path)
                if len(os.listdir(item_path)) == 0:
                    empty_folders.append(item_path)
            elif item.endswith(".csv"):
                try:
                    with open(item_path, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) <= 1:
                            empty_files.append(item_path)
                except:
                    pass
    
    collect_empty_items(movies_folder)
    
    # Second pass: delete collected items
    deleted_count = 0
    
    # Delete empty files
    for file_path in empty_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed empty file: {file_path}")
                deleted_count += 1
        except Exception as e:
            print(f"Error removing file {file_path}: {str(e)}")
    
    # Delete empty folders (deepest first)
    empty_folders.sort(key=lambda x: len(x.split(os.sep)), reverse=True)
    
    all_removed_folders = set()
    
    for folder_path in empty_folders:
        try:
            if (os.path.exists(folder_path) and 
                os.path.isdir(folder_path) and 
                len(os.listdir(folder_path)) == 0 and
                folder_path != movies_folder):
                
                os.rmdir(folder_path)
                print(f"Removed empty folder: {folder_path}")
                deleted_count += 1
                all_removed_folders.add(folder_path)
                
        except Exception as e:
            print(f"Error removing folder {folder_path}: {str(e)}")
    
    # Third pass: check if parent folders became empty and remove them
    print("\nChecking for empty parent folders...")
    additional_removed = check_and_remove_empty_parents(all_removed_folders, movies_folder)
    deleted_count += additional_removed
    
    return deleted_count


def check_and_remove_empty_parents(removed_folders, movies_folder):
    """Check if parent folders became empty after deletions and remove them recursively"""
    deleted_count = 0
    folders_to_check = set(removed_folders)
    all_removed = set()
    
    while folders_to_check:
        current_folder = folders_to_check.pop()
        parent_folder = os.path.dirname(current_folder)
        
        # Skip if we've already processed this parent or it's the main movies folder
        if (parent_folder in all_removed or 
            parent_folder == movies_folder or 
            not os.path.exists(parent_folder)):
            continue
        
        # Check if parent folder is empty
        if (os.path.isdir(parent_folder) and 
            len(os.listdir(parent_folder)) == 0):
            
            try:
                os.rmdir(parent_folder)
                print(f"Removed empty parent folder: {parent_folder}")
                deleted_count += 1
                all_removed.add(parent_folder)
                # Add this parent to the set to check its parent too
                folders_to_check.add(parent_folder)
                
            except Exception as e:
                print(f"Error removing parent folder {parent_folder}: {str(e)}")
    
    return deleted_count



def delete_movie(all_movies):
    """
    Searches for a movie by name, genre, release year and duration category.
    If found, deletes it from memory and CSV files, cleaning up empty files and folders.
    
    Args:
        all_movies (list): List of dictionaries with all movies
    
    Returns:
        list: Updated list of movies
    """
    print("\n--- Delete Movie ---")
    
    # Get search criteria
    name, genre, year, duration_category = get_movie_search_criteria()
    
    # Find movie
    found_movie = find_movie_by_criteria(all_movies, name, genre, year, duration_category)
    if not found_movie:
        print("\nNo movie found that matches all the specified criteria.")
        return all_movies
    
    print(f"\nMovie found!: {found_movie['name']}")
    print("Movie data to be deleted:")
    for field in main.HEADER:
        print(f"  {field}: {found_movie[field]}")
    
    while True:
        # Confirm deletion
        print(f"\nAre you sure you want to delete '{found_movie['name']}'?\n"
            "1. Yes, delete\n"
            "0. No, return")
        confirmation = main.insert_option(range_max=1)
        match confirmation:
            case 1:
                break
            case 0:
                return all_movies
    
    # Remove from memory list
    all_movies.remove(found_movie)
    print(f"\nMovie '{found_movie['name']}' removed from memory.")
    
    # Remove from CSV files
    movies_folder, encoding, file_format, _ = get_config()
    
    try:
        # Track if we found and removed the movie from any file
        movie_removed = False
        
        # First: Collect all CSV files
        files_to_process = []
        
        def collect_csv_files(folder_path):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    collect_csv_files(item_path)
                elif item.endswith(f".{file_format}"):
                    files_to_process.append(item_path)
        
        collect_csv_files(movies_folder)
        
        # Second: Process each file
        for file_path in files_to_process:
            try:
                # Read current movies from file
                movies_data = read_csv_file(file_path, encoding)
                if not movies_data:
                    continue
                
                # Filter out the movie to delete
                updated_movies = []
                file_modified = False
                
                for movie in movies_data:
                    if not movies_are_identical(movie, found_movie):
                        updated_movies.append(movie)
                    else:
                        movie_removed = True
                        file_modified = True
                        print(f"Movie removed from: {file_path}")
                
                # Write updated movies back to file (or delete file if empty)
                if updated_movies:
                    if file_modified:  # Only write if something changed
                        write_csv_file(file_path, updated_movies, encoding, main.HEADER)
                else:
                    # File is now empty, remove it
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Empty file removed: {file_path}")
                        
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
        
        if not movie_removed:
            print("Warning: Movie was not found in any CSV file, but was removed from memory.")
        else:
            print("Movie successfully deleted from all files!")
        
        # Clean up any empty files and folders with the safe function
        print("\nCleaning up empty files and folders...")
        items_cleaned = safe_clean_empty_files_and_folders(movies_folder)
        if items_cleaned > 0:
            print(f"Cleaned up {items_cleaned} empty items")
        else:
            print("No empty items found to clean")
        
    except Exception as e:
        print(f"Error during file deletion: {str(e)}")
        # Note: We don't add the movie back to memory since deletion was confirmed
    
    return all_movies