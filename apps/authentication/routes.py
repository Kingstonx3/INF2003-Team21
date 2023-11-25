from math import e
from flask import render_template, redirect, request, url_for, session, Response
from flask_login import (
    current_user,
    login_user,
    logout_user,
)

from apps import login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm, SettingsForm, ProfileForm
from apps.authentication.models import (get_user_by_username, create_account, update_account, 
                                        get_profiles, get_single_profile, save_image,
                                        update_profile, create_profile, delete_profile, 
                                        get_movie, get_movies_count, update_movie,
                                        delete_movie, create_movie, topup, get_acc_credits,
                                        update_popularity, update_last_watch, update_history_data,
                                        get_popularity, get_last_watch, get_history_data,
                                        get_reviews, update_reviews, get_user_reviews,
                                        get_movie_by_id, get_users, get_users_count,
                                        delete_account, get_account_priv, update_account_priv)
from apps.authentication.util import verify_pass

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.movieListings'))

# Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        # Read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = get_user_by_username(username)

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('authentication_blueprint.profileSelect'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('authentication_blueprint.profileSelect'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        createStatus = create_account(username, email, password)

        # If creation is unsucessfully
        if createStatus != 'success':
            errMsg = ''
            if createStatus == 'username':
                errMsg = 'Username already registered.'
            elif createStatus == 'email':
                errMsg = 'Email already registered.'
            elif createStatus == 'both':
                errMsg = 'Username already registered.\nEmail already registered.'
            else:
                errMsg = 'Something went wrong.'

            return render_template('accounts/register.html',
                                   msg=errMsg,
                                   success=False,
                                   form=create_account_form)
        else:
            # Delete user from session
            logout_user()        

            return render_template('accounts/register.html',
                                msg='User created successfully.',
                                success=True,
                                form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)

# Main page
@blueprint.route('/index', methods=['GET', 'POST'])
def movieListings():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)
    rowSelect = 0

    if (request.args.get('del')):
        delete_movie(request.args.get('del'))
    elif (request.args.get('page')):
        rowSelect = int(request.args.get('page'))

    movies = get_movie(rowSelect)
    movieCount = get_movies_count()
    movieCount = movieCount // 20 + (movieCount%20>0)

    # Set row to 1 from 0 for html to work properly
    if not rowSelect:
        rowSelect = 1

    # Get user account type
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    return render_template('home/index.html',
                            movieData=movies,
                            currentRow=rowSelect,
                            total_pages=movieCount,
                            accountType=current_user.accountStatus,
                            profileType=profileType,
                            accPriv=accPriv)

# Video page
@blueprint.route('/view_video', methods=['GET'])
def view_video():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    if (request.args.get('v')):
        movieName = request.args.get('v')
    else:
        return render_template('home/page-500.html'), 500

    accPriv = get_account_priv(current_user.id)
    movie_data = get_movie(0, movieName)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    # Get Popularity
    moviePop = get_popularity(movie_data['MovieId'])

    # Get Last Watch Timestamp
    lastWatched = get_last_watch(movie_data['MovieId'], current_user.id)

    # Get review stuff
    movieReviews = list(get_reviews(movie_data['MovieId']))

    if movie_data:
        return render_template('home/video.html',
                                movieData=movie_data,
                                moviePop=moviePop,
                                movieReviews=movieReviews,
                                lastWatched=lastWatched,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)
    else:
        return render_template('home/page-500.html'), 500

# Review
@blueprint.route('/submitRating', methods=['POST'])
def submitRating():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    try:
        accPriv = get_account_priv(current_user.id)
        movie_data = get_movie(0, request.form['movieTitle'])
        print(movie_data)
        # Update reviews
        update_reviews(movie_data['MovieId'], current_user.id, session['nickname'],
                       int(request.form['rating']), request.form['review'])

        # Send back to the movie page
        # Get Popularity
        moviePop = get_popularity(movie_data['MovieId'])

        # Get Last Watch Timestamp
        lastWatched = get_last_watch(movie_data['MovieId'], current_user.id)

        # Get review stuff
        movieReviews = get_reviews(movie_data['MovieId'])

        if movie_data:
            return render_template('home/video.html',
                                    movieData=movie_data,
                                    moviePop=moviePop,
                                    movieReviews=movieReviews,
                                    lastWatched=lastWatched,
                                    accPriv=accPriv)
        else:
                return render_template('home/page-500.html'), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(status=204)


# Video data backend storing
@blueprint.route('/videoApi', methods=['POST'])
def videoApi():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    try:
        # Update if at least 5s watched
        if (int(float(request.form['timeWatched'])) > 5):
            # Update Popularity
            update_popularity(int(request.form['movieId']))

            # Update Last Watch timestamp
            update_last_watch(int(request.form['movieId']), current_user.id,
                            int(float(request.form['endTimestamp'])),
                            int(request.form['videoEnd']))

            # Update Historical Data
            update_history_data(int(request.form['movieId']),
                                int(float(request.form['timeWatched'])))
            
            return Response(status=204)
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(status=204)

# Add Movie
@blueprint.route('/add_movie', methods=['GET', 'POST'])
def addMovie():
    if not current_user.is_authenticated or current_user.accountStatus != 5:
        return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    if request.method == 'POST':
        release_date = request.form['release_date']
        metascore = request.form['metascore']
        runtime = request.form['runtime']

        if (release_date.isdigit() and metascore.isdigit() and runtime.isdigit()):
            msg = create_movie(request.form)

            return render_template('admin/add_movie.html',
                                msg=msg,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)
        else:
            return render_template('admin/add_movie.html',
                                msg="Failed to create movie.",
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)
        

    return render_template('admin/add_movie.html',
                           accountType=current_user.accountStatus,
                           profileType=profileType,
                           accPriv=accPriv)

# Edit Movie
@blueprint.route('/modify_movie', methods=['GET', 'POST'])
def modifyMovie():
    if not current_user.is_authenticated or current_user.accountStatus != 5:
        return redirect(url_for('authentication_blueprint.login'))

    if (request.args.get('v')):
        movieName = request.args.get('v')
    else:
        return render_template('home/page-500.html'), 500

    accPriv = get_account_priv(current_user.id)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    if request.method == 'POST':
        release_date = request.form['release_date']
        metascore = request.form['metascore']
        runtime = request.form['runtime']

        if (release_date.isdigit() and metascore.isdigit() and runtime.isdigit()):
            update_movie(request.form)

            movieData = get_movie(0, movieName)
            if movieData:
                msg = "Movie successfully updated."
                return render_template('admin/modify_movie.html',
                                    movieData=movieData,
                                    msg=msg,
                                    accountType=current_user.accountStatus,
                                    profileType=profileType,
                                    accPriv=accPriv)
        else:
            msg = "Failed to update movie."
            movieData = get_movie(0, movieName)
            if movieData:
                return render_template('admin/modify_movie.html',
                                    movieData=movieData,
                                    msg=msg,
                                    accountType=current_user.accountStatus,
                                    profileType=profileType,
                                    accPriv=accPriv)
        

    elif request.method == 'GET':
        movieData = get_movie(0, movieName)
        if movieData:
            return render_template('admin/modify_movie.html',
                                movieData=movieData,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)

    return render_template('home/page-500.html'), 500

# Profile page
@blueprint.route('/profile', methods=['GET', 'POST'])
def profileSelect():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    users = list(get_profiles(current_user.id))
    profile_form = ProfileForm(request.form)

    if 'selectProfile' in request.form:
        profile = get_single_profile(request.form['nickname'])
        pin = profile.get('pin')

        if (pin):
            if verify_pass(request.form['newPin'], pin):
                session['nickname'] = request.form['nickname']
                return redirect(url_for('home_blueprint.index'))
            else:
                return render_template('accounts/pick-profile.html',
                               form=profile_form,
                               userData=users,
                               msg="Wrong Pin!")
        else:
            session['nickname'] = request.form['nickname']
            return redirect(url_for('home_blueprint.index'))

    return render_template('accounts/pick-profile.html',
                               form=profile_form,
                               userData=users)

# Profile setting page
@blueprint.route('/editProfile', methods=['GET', 'POST'])
def profileSetting():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)
    users = list(get_profiles(current_user.id))
    profile_form = ProfileForm(request.form)
    reviews = list(get_user_reviews(current_user.id)) 

    # Get movie for reviews
    movieInfo = {}
    if reviews:
        movieList = [] 
        for review in reviews:
            movieList.append(review['movieId'])
        # Remove dupes
        movieList = list(set(movieList))
        movieInfo = get_movie_by_id(movieList)
        movieInfo = {movie['MovieId']: movie['Title'] for movie in movieInfo}

    profileType = None

    for user in users:
        if user['nickname'] == session.get('nickname'):
            profileType = user['profileType']
            break

    if 'uploadImage' in request.form:
        result = save_image(request.files['profileImage'], request.form['oldNickname'])
        # Get the user's new image
        users = list(get_profiles(current_user.id))

        return render_template('accounts/user-profile.html',
                               form=profile_form,
                               userData=users,
                               msg=result,
                               reviews=reviews,
                               movieInfo=movieInfo,
                               nick=session.get('nickname'),
                               profileType=profileType,
                               accountType=current_user.accountStatus,
                               accPriv=accPriv)

    elif 'updateProfile' in request.form:
        profileUpdates = {'nickname': request.form['oldNickname']}
        if (request.form['nickname'] != profileUpdates['nickname']):
            profileUpdates['newNickname'] = request.form['nickname']
        if (request.form['newPin'] == request.form['newPinConfirm']):
            if (request.form['newPin']):
                profileUpdates['newPin'] = request.form['newPin']

        result = update_profile(profileUpdates)
        # Get the user's new nickname if changed
        users = list(get_profiles(current_user.id))

        return render_template('accounts/user-profile.html',
                               form=profile_form,
                               userData=users,
                               msg=result,
                               reviews=reviews,
                               movieInfo=movieInfo,
                               nick=session.get('nickname'),
                               profileType=profileType,
                               accountType=current_user.accountStatus,
                               accPriv=accPriv)

    elif 'newProfile' in request.form:
        error = False
        if not (request.form['nickname']):
            error = True
        elif (request.form['newPin'] != request.form['newPinConfirm']):
            error = True

        if error:
            msg = "Failed to make a new profile."
            return render_template('accounts/user-profile.html',
                               form=profile_form,
                               userData=users,
                               msg=msg,
                               reviews=reviews,
                               movieInfo=movieInfo,
                               nick=session.get('nickname'),
                               profileType=profileType,
                               accountType=current_user.accountStatus,
                               accPriv=accPriv)

        accountType = True if 'accountType' in request.form else False
        profileCreate = {
            'userId': current_user.id,
            'nickname': request.form['nickname'],
            'pin': request.form['newPin'],
            'profilePicture': '/static/assets/img/defaultprofile.jpg',
            'langPref': 'en',
            'profileType': accountType,
        }

        result = create_profile(profileCreate)
        # Get new profile
        users = list(get_profiles(current_user.id))

        return render_template('accounts/user-profile.html',
                               form=profile_form,
                               userData=users,
                               msg=result,
                               reviews=reviews,
                               movieInfo=movieInfo,
                               nick=session.get('nickname'),
                               profileType=profileType,
                               accountType=current_user.accountStatus,
                               accPriv=accPriv)

    elif 'deleteProfile' in request.form:
            result = delete_profile(request.form['oldNickname'])

            # Get the user's new nickname if changed
            users = list(get_profiles(current_user.id))

            return render_template('accounts/user-profile.html',
                                form=profile_form,
                                userData=users,
                                msg=result,
                                reviews=reviews,
                                movieInfo=movieInfo,
                                nick=session.get('nickname'),
                                profileType=profileType,
                                accountType=current_user.accountStatus,
                                accPriv=accPriv)

    return render_template('accounts/user-profile.html',
                               form=profile_form,
                               userData=users,
                               reviews=reviews,
                               movieInfo=movieInfo,
                               nick=session.get('nickname'),
                               profileType=profileType,
                               accountType=current_user.accountStatus,
                               accPriv=accPriv)

@blueprint.route('/topup', methods=['GET', 'POST'])
def topupAccount():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))
    else:
        profile = get_single_profile(session['nickname'])
        profileType = profile.get('profileType')
        if profileType != 1:
            return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)
    credits = get_acc_credits(current_user.id)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    if request.method == 'POST':
        selectedValue = request.form['selectedValue']

        if selectedValue in ['90', '210', '1080']:
            msg = topup(selectedValue, current_user.id)
            credits = get_acc_credits(current_user.id)

            return render_template('accounts/topup.html',
                                credits=credits,
                                msg=msg,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)
        else:
            return render_template('accounts/topup.html',
                                credits=credits,
                                msg="Failed to top up.",
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)

    return render_template('accounts/topup.html',
                           credits=credits,
                           accountType=current_user.accountStatus,
                           profileType=profileType,
                           accPriv=accPriv)

# Setting page
@blueprint.route('/settings', methods=['GET', 'POST'])
def settings():
    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)
    settings_form = SettingsForm(request.form)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    if 'updateSettings' in request.form:
        # Read form data
        username = request.form['username']
        email = request.form['email']
        confirmPassword = request.form['confirmPassword']
        password = request.form['newPassword']
        passwordConfirm = request.form['newPasswordConfirm']

        if password != passwordConfirm:
            errMsg = 'newPass'
        elif verify_pass(confirmPassword, current_user.password):
            updateStatus = update_account(username, email, password, current_user.username)

        # If creation is unsucessfully
        if updateStatus != 'success':
            errMsg = ''
            if updateStatus == 'username':
                errMsg = 'Username already in use.'
            elif updateStatus == 'email':
                errMsg = 'Email already in use.'
            elif updateStatus == 'both':
                errMsg = 'Username already registered.\nEmail already registered.'
            elif updateStatus == 'newPass':
                errMsg = 'New password does not match with confirmation.'
            elif updateStatus == 'confirmWrong':
                errMsg = 'Confirmation Password is wrong.'
            else:
                errMsg = 'Something went wrong.'

            return render_template('accounts/settings.html',
                                   msg=errMsg,
                                   form=settings_form,
                                   accountType=current_user.accountStatus,
                                   profileType=profileType,
                                   accPriv=accPriv)
        else:
            return render_template('accounts/settings.html',
                                msg='Settings successfully updated.',
                                form=settings_form,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)
    else:
        accData = {
            'username': current_user.username,
            'email': current_user.email
        }

        return render_template('accounts/settings.html',
                               form=settings_form,
                               accData=accData,
                               accountType=current_user.accountStatus,
                               profileType=profileType,
                               accPriv=accPriv)

# Admin page - Movie
@blueprint.route('/adminMovie', methods=['GET', 'POST'])
def adminMoive():
    if not current_user.is_authenticated or current_user.accountStatus != 5:
        return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)

    if not accPriv['moviePerm']:
        return render_template('home/page-403.html'), 403

    rowSelect = 0

    if (request.args.get('del')):
        delete_movie(request.args.get('del'))
    elif (request.args.get('page')):
        rowSelect = int(request.args.get('page'))

    movies = get_movie(rowSelect)
    movieCount = get_movies_count()
    movieCount = movieCount // 20 + (movieCount%20>0)
    historyData = get_history_data(rowSelect)
    if historyData:
        historyData = {movie['movieId']: {'TotalTime': movie['TotalTime'],
                                            'LastUpdated': movie['LastUpdated']}
                                            for movie in historyData}
    else:
        historyData = {}

    # Set row to 1 from 0 for html to work properly
    if not rowSelect:
        rowSelect = 1

    # Get user account type
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    return render_template('admin/adminMovie.html',
                            movieData=movies,
                            currentRow=rowSelect,
                            total_pages=movieCount,
                            accountType=current_user.accountStatus,
                            profileType=profileType,
                            historyData=historyData,
                            accPriv=accPriv)

# Admin page - Accounts
@blueprint.route('/adminAccount', methods=['GET', 'POST'])
def adminAccount():
    if not current_user.is_authenticated or current_user.accountStatus != 5:
        return redirect(url_for('authentication_blueprint.login'))
    
    accPriv = get_account_priv(current_user.id)
    if not accPriv['accPerm']:
        return render_template('home/page-403.html'), 403

    rowSelect = 0

    if (request.args.get('del')):
        delete_account(request.args.get('del'))
        if request.args.get('del') == current_user.username:
            render_template('/logout')
    elif (request.args.get('page')):
        rowSelect = int(request.args.get('page'))

    users = get_users(rowSelect)
    userCount = get_users_count()
    userCount = userCount // 20 + (userCount%20>0)

    # Set row to 1 from 0 for html to work properly
    if not rowSelect:
        rowSelect = 1

    # Get user account type
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    return render_template('admin/adminAccount.html',
                            userData=users,
                            currentRow=rowSelect,
                            total_pages=userCount,
                            accountType=current_user.accountStatus,
                            profileType=profileType,
                            accPriv=accPriv)

# Add User
@blueprint.route('/addUser', methods=['GET', 'POST'])
def addUser():
    if not current_user.is_authenticated or current_user.accountStatus != 5:
        return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    if request.method == 'POST':
        accStatus = request.form['accStatus']
        accCredits = request.form['accCredits']

        if (accStatus.isdigit() and accCredits.isdigit()):
            if (int(accStatus) < 6):
                updateStatus = create_account(request.form['username'],
                                    request.form['email'],
                                    request.form['password'],
                                    request.form)

                # If creation is unsucessfully
                if updateStatus != 'success':
                    if updateStatus == 'username':
                        updateStatus = 'Username already in use.'
                    elif updateStatus == 'email':
                        updateStatus = 'Email already in use.'
                    elif updateStatus == 'both':
                        updateStatus = 'Username already registered.\nEmail already registered.'
                    else:
                        updateStatus = 'Something went wrong.'

                return render_template('admin/add_user.html',
                                        accountType=current_user.accountStatus,
                                        msg=updateStatus,
                                        profileType=profileType,
                                        accPriv=accPriv)

        return render_template('admin/add_user.html',
                               accountType=current_user.accountStatus,
                               msg="Failed to add user.",
                               profileType=profileType,
                               accPriv=accPriv)

    return render_template('admin/add_user.html',
                           accountType=current_user.accountStatus,
                           profileType=profileType,
                           accPriv=accPriv)

# Edit User
@blueprint.route('/modifyUser', methods=['GET', 'POST'])
def modifyUser():
    if not current_user.is_authenticated or current_user.accountStatus != 5:
        return redirect(url_for('authentication_blueprint.login'))

    accPriv = get_account_priv(current_user.id)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    if (request.args.get('u')):
        accountName = request.args.get('u')
    else:
        return render_template('home/page-500.html'), 500

    if request.method == 'POST':
        accStatus = request.form['accStatus']
        accCredits = request.form['accCredits']

        if (accStatus.isdigit() and accCredits.isdigit()):
            if (int(accStatus) < 6):
                updateStatus = update_account(request.form['username'],
                                    request.form['email'],
                                    request.form['password'],
                                    accountName,
                                    request.form)

                # If creation is unsucessfully
                if updateStatus != 'success':
                    errMsg = ''
                    if updateStatus == 'username':
                        errMsg = 'Username already in use.'
                    elif updateStatus == 'email':
                        errMsg = 'Email already in use.'
                    elif updateStatus == 'both':
                        errMsg = 'Username already registered.\nEmail already registered.'
                    elif updateStatus == 'newPass':
                        errMsg = 'New password does not match with confirmation.'
                    elif updateStatus == 'confirmWrong':
                        errMsg = 'Confirmation Password is wrong.'
                    else:
                        errMsg = 'Something went wrong.'

                    userData = get_user_by_username(accountName, 'admin')
                    if userData:
                        return render_template('admin/modify_user.html',
                                            userData=userData,
                                            accountType=current_user.accountStatus,
                                            profileType=profileType,
                                            msg=errMsg,
                                            accPriv=accPriv)
                else:
                    userData = get_user_by_username(request.form['username'], 'admin')
                    if userData:
                        msg = "User successfully updated."
                        return render_template('admin/modify_user.html',
                                            userData=userData,
                                            accountType=current_user.accountStatus,
                                            profileType=profileType,
                                            msg=msg,
                                            accPriv=accPriv)

        msg = "Failed to update user."
        userData = get_user_by_username(accountName, 'admin')
        if userData:
            return render_template('admin/modify_user.html',
                                userData=userData,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                msg=msg,
                                accPriv=accPriv)
        
    elif request.method == 'GET':
        userData = get_user_by_username(accountName, 'admin')
        if userData:
            return render_template('admin/modify_user.html',
                                userData=userData,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                accPriv=accPriv)

    print("Request: ", request.method)
    return render_template('home/page-500.html'), 500

# Modify Privilege
@blueprint.route('/modifyUserPriv', methods=['GET', 'POST'])
def modifyUserPriv():
    if not current_user.is_authenticated or current_user.accountStatus != 5:
        return redirect(url_for('authentication_blueprint.login'))

    if (request.args.get('u')):
        username = request.args.get('u')
        userId = get_user_by_username(username, 'admin')['UserId']
    else:
        return render_template('home/page-500.html'), 500

    accPriv = get_account_priv(current_user.id)
    profile = get_single_profile(session['nickname'])
    profileType = profile.get('profileType')

    if request.method == 'POST':
        moviePerm = True if 'moviePerm' in request.form else False
        accPerm = True if 'accPerm' in request.form else False
        msg = update_account_priv(userId, moviePerm, accPerm)
        if not msg:
            msg = "Failed to modify account privileges."

        userData = get_account_priv(userId)

        return render_template('admin/modify_user_privilege.html',
                                userData=userData,
                                username=username,
                                accountType=current_user.accountStatus,
                                profileType=profileType,
                                msg=msg,
                                accPriv=accPriv)

    elif request.method == 'GET':
        userData = get_account_priv(userId)

        return render_template('admin/modify_user_privilege.html',
                            userData=userData,
                            username=username,
                            accountType=current_user.accountStatus,
                            profileType=profileType,
                            accPriv=accPriv)

    return render_template('home/page-500.html'), 500

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))

# Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
