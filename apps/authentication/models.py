from flask_login import UserMixin
from apps import mysql, login_manager, mongo
from apps.authentication.util import hash_pass
from datetime import datetime
import os
import time

class User(UserMixin):
    def __init__(self, id, username, email, password, accountStatus, watchCredits):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.accountStatus = accountStatus
        self.watchCredits = watchCredits
    
    def get_id(self):
        return str(self.username)

def get_user_by_username(username, type=None):
    try:
        with mysql.db.cursor() as cursor:
            query = "SELECT * FROM UserAccount WHERE Username = %s"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()
            if user_data:
                if type == 'admin':
                    return user_data
                else:
                    id, username, email, password, accountStatus, watchCredits = user_data.values()
                    return User(id, username, email, password, accountStatus, watchCredits)
            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_users(row):
    try:
        with mysql.db.cursor() as cursor:
            query = "SELECT * FROM UserAccount LIMIT 20 OFFSET " + str(row*20)
            cursor.execute(query)
            user_data = cursor.fetchall()
            if user_data:
                return user_data
            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def delete_user(username):
    try:
        with mysql.db.cursor() as cursor:
            query = "DELETE FROM UserAccount WHERE Username = %s"
            cursor.execute(query, (username,))
            mysql.db.commit()

            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_users_count():
    try:
        with mysql.db.cursor() as cursor:
            query = "SELECT COUNT(*) FROM UserAccount"
            cursor.execute(query)
            user_data = cursor.fetchall()
            if user_data:
                return user_data[0]['COUNT(*)']
            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None


def get_movie(row, movieName=None):
    try:
        with mysql.db.cursor() as cursor:
            if (movieName):
                query = "SELECT * FROM MovieInfo WHERE Title = %s"
                cursor.execute(query, (movieName,))
                movie_data = cursor.fetchone()
                if movie_data:
                    return movie_data
            else:
                query = "SELECT * FROM MovieInfo LIMIT 20 OFFSET " + str(row*20)
                cursor.execute(query)
                movie_data = cursor.fetchall()
                if movie_data:
                    return movie_data
            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_movie_by_id(movieId):
    try:
        with mysql.db.cursor() as cursor:
            print(movieId)
            tempStr = ', '.join(['%s'] * len(movieId))
            query = f"SELECT * FROM MovieInfo WHERE MovieId IN ({tempStr})"
            cursor.execute(query, tuple(movieId))
            movie_data = cursor.fetchall()
            if movie_data:
                return movie_data
            else:
                return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def create_movie(movie_data):
    try:
        with mysql.db.cursor() as cursor:
            # Check if Movie exist
            query = "SELECT * FROM MovieInfo WHERE Title = %s"
            cursor.execute(query, (movie_data['title'],))
            movie_info = cursor.fetchone()
            if movie_info:
                return "Movie name already exists."

            # Create Movie
            query = "INSERT INTO MovieInfo (Title, Genre, Description, \
                Director, Actors, Year, `Runtime (Minutes)`, \
                Metascore, TrailerUrl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (movie_data['title'], movie_data['genre'],
                                   movie_data['plot_summary'], movie_data['director'],
                                   movie_data['actors'], int(movie_data['release_date']),
                                   int(movie_data['runtime']), int(movie_data['metascore']),
                                   movie_data['trailer_url'],))
            mysql.db.commit()

            return "Movie successfully created."
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def update_movie(movie_data):
    try:
        with mysql.db.cursor() as cursor:
            query = "UPDATE MovieInfo SET Title = %s, Genre = %s, Description = %s, \
                Director = %s, Actors = %s, Year = %s, `Runtime (Minutes)` = %s, \
                Metascore = %s, TrailerUrl = %s WHERE Title = %s"
            cursor.execute(query, (movie_data['title'], movie_data['genre'],
                                   movie_data['plot_summary'], movie_data['director'],
                                   movie_data['actors'], int(movie_data['release_date']),
                                   int(movie_data['runtime']), int(movie_data['metascore']),
                                   movie_data['trailer_url'], movie_data['title'],))
            mysql.db.commit()

            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def delete_movie(movie_name):
    try:
        with mysql.db.cursor() as cursor:
            query = "DELETE FROM MovieInfo WHERE Title = %s"
            cursor.execute(query, (movie_name,))
            mysql.db.commit()

            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_movies_count():
    try:
        with mysql.db.cursor() as cursor:
            query = "SELECT COUNT(*) FROM MovieInfo"
            cursor.execute(query)
            movie_count = cursor.fetchall()
            if movie_count:
                return movie_count[0]['COUNT(*)']
            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def create_account(username, email, password, form=None):
    try:
        with mysql.db.cursor() as cursor:
            # Check if Username exist
            errMsg = ''
            query = "SELECT * FROM UserAccount WHERE Username = %s"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()
            if user_data:
                errMsg = 'username'

            # Check if Email exist
            query = "SELECT * FROM UserAccount WHERE Email = %s"
            cursor.execute(query, (email,))
            user_data_email = cursor.fetchone()
            if user_data_email:
                if errMsg == 'username':
                    errMsg = 'both'
                else:
                    errMsg = 'email'
            
            # If Username or Email exist, return error
            if errMsg:
                cursor.close()
                return errMsg

            # If creating from admin page
            if form:
                query = "INSERT INTO UserAccount (Username, Email, Password, AccountStatus, \
                WatchCredits) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (username, email, hash_pass(password),
                                       int(form['accStatus']), int(form['accCredits'])))
                mysql.db.commit()
            else:
                # Create account
                query = "INSERT INTO UserAccount (Username, Email, Password) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, email, hash_pass(password)))
                mysql.db.commit()

            # Create Profile
            query = "SELECT UserId FROM UserAccount WHERE Username = %s"
            cursor.execute(query, (username,))
            user_id = cursor.fetchone()['UserId']
            mongo.db.UserProfile.insert_one({
                'userId': user_id,
                'nickname': username,
                'profilePicture': '/static/assets/img/defaultprofile.jpg',
                'langPref': 'en',
                'profileType': 1,
            })

            return 'success'

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def update_account(username, email, password, oldUsername, form=None):
    try:
        with mysql.db.cursor() as cursor:
            errMsg = ''

            # Check if username exist if there is input
            if username:
                query = "SELECT * FROM UserAccount WHERE Username = %s"
                cursor.execute(query, (username,))
                user_data = cursor.fetchone()
                if user_data:
                    if not form:
                        errMsg = 'username'
                    else:
                        username = None
                else:
                    query = "UPDATE UserAccount SET Username = %s WHERE Username = %s"
                    cursor.execute(query, (username, email,))
                    mysql.db.commit()

            # Check if email exist if there is input
            if email:
                query = "SELECT * FROM UserAccount WHERE Email = %s"
                cursor.execute(query, (email,))
                user_data_email = cursor.fetchone()
                if user_data_email:
                    if not form:
                        if errMsg == 'username':
                            errMsg = 'both'
                        else:
                            errMsg = 'email'
                    else:
                        email = None

            # If Username or Email exist, return error
            if errMsg:
                cursor.close()
                return errMsg

            # Update username
            if username:
                if not form:
                    query = "UPDATE UserAccount SET Username = %s WHERE Username = %s"
                    cursor.execute(query, (username, oldUsername,))
                elif username != oldUsername:
                    query = "UPDATE UserAccount SET Username = %s WHERE Username = %s"
                    cursor.execute(query, (username, oldUsername,))

            # Update email
            if email:
                query = "UPDATE UserAccount SET email = %s WHERE Username = %s"
                cursor.execute(query, (username, oldUsername,))

            # Update password
            if password:
                query = "UPDATE UserAccount SET password = %s WHERE Username = %s"
                cursor.execute(query, (hash_pass(password), oldUsername,))
            
            # Update Status / Credits
            if form:
                if form['accStatus']:
                    query = "UPDATE UserAccount SET AccountStatus = %s WHERE Username = %s"
                    cursor.execute(query, (int(form['accStatus']), oldUsername,))
                if form['accCredits']:
                    query = "UPDATE UserAccount SET WatchCredits = %s WHERE Username = %s"
                    cursor.execute(query, (int(form['accCredits']), oldUsername,))

            mysql.db.commit()
            return 'success'

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def delete_account(account_name):
    try:
        with mysql.db.cursor() as cursor:
            query = "DELETE FROM UserAccount WHERE Username = %s"
            cursor.execute(query, (account_name,))
            mysql.db.commit()

            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_profiles(userId):
    return mongo.db.UserProfile.find({"userId": userId})

def get_single_profile(nickname):
    return mongo.db.UserProfile.find_one({"nickname": nickname})

def save_image(image, nickname):
    # TODO: Function to secure filename.
    file_path = os.path.join('apps/static/assets/img/upload/', image.filename)

    results = mongo.db.UserProfile.update_one(
        {'nickname': nickname},
        {'$set': {'profilePicture': file_path[5:]}}
    )

    if results.modified_count > 0:
        image.save(file_path)

        return "Profile image successfully changed. It may take awhile to change."
    else:
        return "Profile image failed to changed."

def update_profile(updateDic):
    resultCode = 0

    if updateDic.get('newNickname'):
        results = mongo.db.UserProfile.update_one(
            {'nickname': updateDic['nickname']},
            {'$set': {'nickname': updateDic['newNickname']}}
        )
        if results.modified_count > 0:
            resultCode = 1

    if updateDic.get('newPin'):
        newPin = hash_pass(updateDic['newPin']).decode('utf-8')

        results = mongo.db.UserProfile.update_one(
            {'nickname': updateDic['nickname']},
            {'$set': {'pin': newPin}}
        )
        if results.modified_count > 0:
            if resultCode == 1:
                resultCode = 3
            else:
                resultCode = 2

    if resultCode > 0:
        if resultCode == 1:
            return "Nickname changed successfully."
        elif resultCode == 2:
            return "Pin changed successfully."
        elif resultCode == 3:
            return "Nickname and Pin changed successfully."
    else:
        return "Failed to update profile."

def create_profile(createDic):
    if mongo.db.UserProfile.find_one({'nickname': createDic['nickname']}):
        return "Nickname already exist."

    newPin = hash_pass(createDic['pin']).decode('utf-8')
    profileType = 2 if createDic['profileType'] else 3

    results = mongo.db.UserProfile.insert_one({
                'userId': createDic['userId'],
                'nickname': createDic['nickname'],
                'pin': newPin,
                'profilePicture': '/static/assets/img/defaultprofile.jpg',
                'langPref': 'en',
                'profileType': profileType,
            })

    if results.inserted_id:
        return "Profile created successfully."
    else:
        return "Failed to create profile."

def delete_profile(nickname):
    results = mongo.db.UserProfile.delete_one({'nickname': nickname})

    if results.deleted_count == 1:
        return "Profile deleted."
    else:
        return "Something went wrong."

def topup(selectedValue, accountId):
    try:
        with mysql.db.cursor() as cursor:
            query = "UPDATE UserAccount SET WatchCredits = %s WHERE UserId = %s"
            cursor.execute(query, (selectedValue, accountId,))        
            mysql.db.commit()

            return 'Account successfully topped up!'

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_acc_credits(accountId):
    try:
        with mysql.db.cursor() as cursor:
            query = "SELECT WatchCredits FROM UserAccount WHERE UserId = %s"
            cursor.execute(query, (accountId,))

            return cursor.fetchone()

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_reviews(movieId):
    return mongo.db.reviews.find({'movieId': movieId})

def get_user_reviews(userId):
    return mongo.db.reviews.find({'userId': userId})

def update_reviews(movieId, userId, nickname, ratings, comment):
    try:
        movieItem = mongo.db.reviews.find_one({'movieId': movieId, 'userId': userId})

        # If row exists else make one
        if movieItem:
            mongo.db.reviews.update_one({
                'movieId': movieId,
                'userId': userId},
                {'$set': {'Nickname': nickname,
                'Rating': ratings,
                'Comment': comment}})
        else:
            mongo.db.reviews.insert_one({
                'movieId': movieId,
                'userId': userId,
                'Nickname': nickname,
                'Rating': ratings,
                'Comment': comment})

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_popularity(movieId):
    return mongo.db.popularity.find_one({'movieId': movieId})

def update_popularity(movieId):
    try:
        movieItem = mongo.db.popularity.find_one({'movieId': movieId})

        # If row exists else make one
        if movieItem:
            mongo.db.popularity.update_one({
                'movieId': movieId},
                {'$inc': {'NumberOfClicks': 1}})
        else:
            mongo.db.popularity.insert_one({
                'movieId': movieId},
                {'$inc': {'NumberOfClicks': 1}})

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def update_popularity(movieId):
    try:
        movieItem = mongo.db.popularity.find_one({'movieId': movieId})

        # If row exists else make one
        if movieItem:
            mongo.db.popularity.update_one({
                'movieId': movieId},
                {'$inc': {'NumberOfClicks': 1}})
        else:
            mongo.db.popularity.insert_one({
                'movieId': movieId},
                {'$inc': {'NumberOfClicks': 1}})

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_last_watch(movieId, userId):
    return mongo.db.lastWatchTime.find_one({'movieId': movieId, 'userId': userId})

def update_last_watch(movieId, userId, timestamp, videoEnd):
    try:
        lastWatchItem = mongo.db.lastWatchTime.find_one({'movieId': movieId, 'userId': userId})
        timestamp = 0 if videoEnd else timestamp

        # If row exists else make one
        if lastWatchItem:
            mongo.db.lastWatchTime.update_one({
                'userId': userId,
                'movieId': movieId},
                {'$set': {'Timestamp': timestamp}})
        else:
            mongo.db.lastWatchTime.insert_one({
                'userId': userId,
                'movieId': movieId,
                'Timestamp': timestamp})

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_history_data(row):
    movies = mongo.db.historyData.find().skip(row * 20).limit(20)
    movie_data = [movie for movie in movies]

    if (movie_data):
        return movie_data
    else:
        return None

def update_history_data(movieId, timewatch):
    try:
        historyData = mongo.db.historyData.find_one({'movieId': movieId})
        timeStamp = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

        # If row exists else make one
        if historyData:
            mongo.db.historyData.update_one({
                'movieId': movieId},
                {'$set': {'LastUpdated': timeStamp},
                '$inc': {'TotalTime': timewatch}})
        else:
            mongo.db.historyData.insert_one({
                'movieId': movieId,
                'LastUpdated': timeStamp},
                {'$inc': {'TotalTime': timewatch}})

    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

def get_account_priv(userId):
    return mongo.db.adminPriv.find_one({'userId': userId})

def update_account_priv(userId, moviePerm, accPerm):
    try:
        historyData = mongo.db.adminPriv.find_one({'userId': userId})

        # If row exists else make one
        if historyData:
            mongo.db.adminPriv.update_one({
                'userId': userId},
                {'$set': {'moviePerm': moviePerm,
                          'accPerm' : accPerm}})
        else:
            mongo.db.adminPriv.insert_one({
                'userId': userId,
                'moviePerm': moviePerm,
                'accPerm' : accPerm})

        return "Privileges successfully modified."
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None

@login_manager.user_loader
def user_loader(username):
    return get_user_by_username(username)

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    try:
        with mysql.db.cursor() as cursor:
            # Check if Username exist
            query = "SELECT * FROM UserAccount WHERE Username = %s"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()
            if user_data:
                user = user_data
                return user
            return None
    except Exception as e:
        print(f"Error while fetching user: {str(e)}")
        return None
