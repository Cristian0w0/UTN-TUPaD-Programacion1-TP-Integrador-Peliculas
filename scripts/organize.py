import main, os



def move_file(source_path, destination_path):
    # Move file from one location to another
    try:
        # Read content from original file
        with open(source_path, "rb", newline="") as source_file:
            content = source_file.read()
        
        # Write content to new location
        with open(destination_path, "wb", newline="") as destination_file:
            destination_file.write(content)
        
        # Delete original file
        os.remove(source_path)
        
        print(f"File moved: {source_path} -> {destination_path}")
        
    except Exception as e:
        print(f"Error moving file {source_path}: {e}")



def search_files(directory, found_files=None):
    # Recursively search for CSV files in directory
    if found_files is None:
        found_files = {}
    
    try:
        # Iterate through all directory elements
        for element in os.listdir(directory):
            full_path = os.path.join(directory, element)
            
            if os.path.isdir(full_path):
                # Recursive call for subdirectories
                search_files(full_path, found_files)
            elif os.path.isfile(full_path) and element.lower().endswith(".csv"):
                # Store found CSV file
                found_files[element.lower()] = full_path
                
    except PermissionError:
        print(f"No permission to access: {directory}")
    
    return found_files



def organize_files():
    # Main function to organize system files
    
    # Get configurations from config file
    path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
    encoding = main.config["Config"]["Encoding"]
    file_format = main.config["Config"]["File_Format"]

    print(f"\nStarting {file_format} file organization...")
    
    # Get base directory
    base_directory = os.getcwd()

    try:
        movies_folder = os.path.join(base_directory, path_movies_unscrapped.split("\\")[0])
        
        # Check if exists, if not create it
        if not os.path.exists(movies_folder):
            os.makedirs(movies_folder)
            print(f"'Movies' folder created: {movies_folder}")
        else:
            print(f"'Movies' folder processed: {movies_folder}")

    except Exception as e:
        print(f"Error: {e}")
        return None

    organized_paths = {}

    # Define expected locations for each file
    expected_locations = {
        "movies_unscrapped." + file_format: os.path.join(base_directory, path_movies_unscrapped),
    }
    
    # Search for all data files in directory
    print(f"Searching for {file_format} files...")
    found_files = search_files(base_directory)
    
    # Process each expected file
    for expected_file, destination_path in expected_locations.items():
        name_without_extension = expected_file.replace("." + file_format, "")
        
        if expected_file in found_files:
            # File found - move if necessary
            found_path = found_files[expected_file]
            
            if found_path != destination_path:
                # Create destination directory if it doesn't exist
                destination_directory = os.path.dirname(destination_path)
                if not os.path.exists(destination_directory):
                    os.makedirs(destination_directory)
                
                # Move file to correct location
                move_file(found_path, destination_path)
            
            organized_paths[name_without_extension] = destination_path
            print(f"Processed: {expected_file}")
            
        else:
            # File not found - create new one
            destination_directory = os.path.dirname(destination_path)
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
            
            try:
                # Create file with default header
                with open(destination_path, "w", encoding=encoding, newline="") as f:
                    f.writelines(",".join(main.HEADER))
                organized_paths[name_without_extension] = destination_path
                print(f"Created: {destination_path}")
            except Exception as e:
                print(f"Error creating {destination_path}: {e}")
    
    print("Organization completed!")
    return organized_paths