import main, os



def show_movies(all_movies):
    """Display all movies with their file paths"""
    if not all_movies:
        print("\nNo movies to display")
        return
    print("\n-- Showing all movies with their location --")
    path_movies_unscrapped = main.config["Movies"]["Movies_Unscrapped"]
    movies_folder = os.getcwd() + "\\" + path_movies_unscrapped.split("\\")[0]
    print(main.HEADER)
    for movie in all_movies:
        # Build the file path based on movie attributes
        path_attributes = [
            movies_folder,
            movie[main.HEADER[1]],
            movie[main.HEADER[2]],
            main.get_duration_category(movie[main.HEADER[3]])
        ]
        movie_path = "\\".join(path_attributes)
        print("")
        print(list(movie.values()))
        print(f"Location: {movie_path}")



def show_movie_amount(all_movies):
    """Display total number of movies"""
    if not all_movies:
        print("\nNo movies to count")
        return
    print(f"\n-- Total number of movies: {len(all_movies)} --")



def show_movie_amount_genre(all_movies):
    """Display number of movies by genre"""
    if not all_movies:
        print("\nNo movies to count by genre")
        return
    
    # Initialize counter for all genres
    genre_amount = {genre: 0 for genre in main.GENRES}
    
    # Count movies per genre
    for movie in all_movies:
        movie_genre = movie[main.HEADER[1]]
        genre_amount[movie_genre] += 1
    
    print("\n-- Number of movies by genre --")
    for genre, amount in genre_amount.items():
        print(f"{genre}: {amount}")



def show_average_duration(all_movies):
    """Calculate and display average duration of all movies"""
    if not all_movies:
        print("\nNo movies to calculate average duration")
        return
    
    total_duration = 0
    movie_amount = len(all_movies)
    
    # Sum all movie durations
    for movie in all_movies:
        movie_duration = movie[main.HEADER[3]]
        total_duration += int(movie_duration)
    
    average_duration = total_duration / movie_amount
    print(f"\n-- Average duration of all movies: {average_duration:.2f} minutes --")



def show_average_duration_genre(all_movies):
    """Calculate and display average duration by genre"""
    if not all_movies:
        print("\nNo movies to calculate average duration by genre")
        return
    
    genre_duration_amount = {}
    
    for movie in all_movies:
        movie_genre = movie[main.HEADER[1]]  # genre
        movie_duration = movie[main.HEADER[3]]  # duration
        
        # Convert duration to integer
        try:
            movie_duration = int(movie_duration)
        except (ValueError, TypeError):
            continue  # Skip if cannot convert to integer
        
        # Initialize genre if it doesn't exist
        if movie_genre not in genre_duration_amount:
            genre_duration_amount[movie_genre] = {
                main.HEADER[3]: 0,
                "amount": 0
            }
        
        # Accumulate duration and count
        genre_duration_amount[movie_genre][main.HEADER[3]] += movie_duration
        genre_duration_amount[movie_genre]["amount"] += 1
    
    # Calculate averages and display results
    print("\n--- Average movie duration by genre ---")
    for genre, data in genre_duration_amount.items():
        average_duration = data[main.HEADER[3]] / data["amount"]
        print(f"{genre}: {average_duration:.2f} minutes")



def show_sorted_movies(all_movies):
    """Display movies sorted by a selected attribute"""
    if not all_movies:
        print("\nNo movies to sort by attribute")
        return
    
    attribute = ""
    while True:
        # Display sorting options menu
        print("\n-- Choose attribute to sort movies --\n"
        "1. Name\n"
        "2. Genre\n"
        "3. Release year\n"
        "4. Duration in minutes\n"
        "5. Rating\n"
        "6. Director\n"
        "7. Original language\n"
        "0. Return to main menu")
        option = main.insert_option(range_max=7)
        match option:
            case 1|2|3|4|5|6|7:
                attribute = main.HEADER[option-1]
                break
            case 0:
                return
    
    # Sort movies by selected attribute
    sorted_movies = sorted(all_movies, key=lambda x: x[attribute])
    print(f"\n-- Movies sorted by {attribute.capitalize()} --")
    print(main.HEADER)
    for movie in sorted_movies:
        print(list(movie.values()))



def show_filtered_movies(all_movies):
    """Display movies filtered by various criteria"""
    if not all_movies:
        print("\nNo movies to filter by attribute")
        return
    
    filtered_movies = []
    filter_condition = ""
    attribute = ""
    
    # Get filter attribute from user
    while True:
        print("\n-- Choose attribute to filter movies --\n"
        "1. Genre\n"
        "2. Release year range\n"
        "3. Duration range in minutes\n"
        "4. Rating range\n"
        "5. Director\n"
        "6. Original language\n"
        "0. Return to main menu")
        option = main.insert_option(range_max=6)
        match option:
            case 1|2|3|4|5|6:
                attribute = main.HEADER[option]
                break
            case 0:
                return
    
    # Filter by genre
    genre = ""
    if attribute == main.HEADER[1]:  # HEADER[1] is genre
        while True:
            print("\n--- Choose genre to filter movies ---")
            for i, genre_item in enumerate(main.GENRES, 1):
                print(f"{i}. {genre_item}")
            print("0. Return to main menu")
            option = main.insert_option(range_max=16)
            match option:
                case _ if 1 <= option <= 16:
                    genre = main.GENRES[option-1]
                    break
                case 0:
                    return
        filter_condition = f"{attribute} ({genre})"
        for movie in all_movies:
            if (movie[attribute] == genre):
                filtered_movies.append(movie)
    
    # Filter by year range
    elif attribute == main.HEADER[2]:  # HEADER[2] is year
        print(f"\n--- Filter by {attribute} range ---")
        try:
            #year_min = int(input("Minimum year: "))
            year_min = main.insert_option(text = "Minimum year: ")
            #year_max = int(input("Maximum year: "))
            year_max = main.insert_option(text = "Maximum year: ")
            
            # Swap if min > max
            if year_min > year_max:
                year_min, year_max = year_max, year_min
                
            filter_condition = f"{attribute} ({year_min}-{year_max})"
            for movie in all_movies:
                movie_year = int(movie[attribute])
                if year_min <= movie_year <= year_max:
                    filtered_movies.append(movie)
        except ValueError:
            print("Error: You must enter valid numbers for years")
            return
    
    # Filter by duration range
    elif attribute == main.HEADER[3]:  # HEADER[3] is duration
        print(f"\n--- Filter by {attribute} range (minutes) ---")
        try:
            #duration_min = int(input("Minimum duration (minutes): "))
            duration_min = main.insert_option(text = "Minimum duration (minutes): ")
            #duration_max = int(input("Maximum duration (minutes): "))
            duration_max = main.insert_option(text = "Maximum duration (minutes): ")
            
            # Swap if min > max
            if duration_min > duration_max:
                print("Minimum duration is bigger than Maximum duration, swapping...")
                duration_min, duration_max = duration_max, duration_min
                
            filter_condition = f"{attribute} ({duration_min}-{duration_max} minutes)"
            for movie in all_movies:
                movie_duration = int(movie[attribute])
                if duration_min <= movie_duration <= duration_max:
                    filtered_movies.append(movie)
        except ValueError:
            print("Error: You must enter valid numbers for duration")
            return
    
    # Filter by rating range
    elif attribute == main.HEADER[4]:  # HEADER[4] is rating
        print(f"\n--- Filter by {attribute} range (1-10) ---")
        try:
            #rating_min = float(input("Minimum rating (1-10): "))
            rating_min = main.insert_option(text = "Minimum rating (1 to 10): ",
                                            range_min = 1,
                                            range_max = 10,
                                            value_type = float)
            #rating_max = float(input("Maximum rating (1-10): "))
            rating_max = main.insert_option(text = "Maximum rating (1 to 10): ",
                                            range_min = 1,
                                            range_max = 10,
                                            value_type = float)
            
            # Swap if min > max
            if rating_min > rating_max:
                print("Minimum rating is bigger than Maximum rating, swapping...")
                rating_min, rating_max = rating_max, rating_min
                
            # Validate rating range
            if rating_min < 0 or rating_max > 10:
                print("Error: Rating must be between 0 and 10")
                return
                
            filter_condition = f"{attribute} ({rating_min}-{rating_max})"
            for movie in all_movies:
                movie_rating = float(movie[attribute])
                if rating_min <= movie_rating <= rating_max:
                    filtered_movies.append(movie)
        except ValueError:
            print("Error: You must enter valid numbers for rating")
            return
    
    # Filter by director (partial match)
    elif attribute == main.HEADER[5]:  # HEADER[5] is director
        print(f"\n--- Filter by {attribute} ---")
        director_search = input("Enter director name: ").strip()
        
        if not director_search:
            print("Error: You must enter a director name")
            return
            
        filter_condition = f"{attribute} ({director_search})"
        for movie in all_movies:
            movie_director = movie[attribute]
            if director_search.lower() in movie_director.lower():
                filtered_movies.append(movie)
    
    # Filter by language (exact match)
    elif attribute == main.HEADER[6]:  # HEADER[6] is language
        print(f"\n--- Filter by {attribute} ---")
        print("Available languages:", ", ".join(sorted(main.LANGUAGES)))
        language_search = input("Enter language: ").strip()
        
        if not language_search:
            print("Error: You must enter a language")
            return
            
        # Validate language input
        if language_search not in main.LANGUAGES:
            print(f"Error: Language '{language_search}' is not in the available languages list")
            return
            
        filter_condition = f"{attribute} ({language_search})"
        for movie in all_movies:
            movie_language = movie[attribute]
            if movie_language == language_search:
                filtered_movies.append(movie)
    
    # Display filtered results
    print(f"\n--- Movies filtered by {filter_condition} ---")
    if not filtered_movies:
        print("No movies match the filter criteria")
    else:
        for movie in filtered_movies:
            print(list(movie.values()))