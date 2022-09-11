# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_AS_ASCII"] = False

db = SQLAlchemy(app)
api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
movies = db.relationship("Movie", cascade="save-update, merge, delete")

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    movies = db.relationship("Movie", cascade="save-update, merge, delete")

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()



genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()
    director = fields.Nested(DirectorSchema)
    genre = fields.Nested(GenreSchema)


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        """
        выводит список всех фильмов, можно задать фильтр в адресной строке по параметрам director_id и genre_id
        :return:
        """
        limit = 4
        director_id_req = request.args.get('director_id')
        genre_id_req = request.args.get('genre_id')
        page = int(request.args.get('page', 1))

        query = db.session.query(Movie)

        if director_id_req:
            query = query.filter(Movie.director_id == director_id_req)
        if genre_id_req:
            query = query.filter(Movie.genre_id == genre_id_req)

        all_movies = query.all()
        items_to_show = all_movies[(page - 1) * limit: page * limit]
        return movies_schema.dump(items_to_show), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)

        return "", 201


@movies_ns.route('/<int:uid>')
class MoviesView(Resource):
    def get(self, uid):
        """
        выводит фильм по его id
        :param uid:
        :return:
        """
        try:
            movie_query = db.session.query(Movie).get(uid)
            return movie_schema.dump(movie_query), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        """
        обновляет данные фильма
        :param uid:
        :return:
        """
        try:
            movie = db.session.query(Movie).get(uid)
            movie_req = request.json
            movie.title = movie_req.get("title")
            movie.description = movie_req.get("description")
            movie.trailer = movie_req.get("trailer")
            movie.year = movie_req.get("year")
            movie.rating = movie_req.get("rating")
            movie.genre_id = movie_req.get("genre_id")
            movie.director_id = movie_req.get("director_id")
            db.session.add(movie)
            db.session.commit()
            return "", 204
        except Exception as e:
            # db.session.rollback()
            return str(e), 404

    def delete(self, uid):
        """
        удаляет данные фильма
        :param uid:
        :return:
        """
        try:
            movie_del = db.session.query(Movie).get(uid)
            db.session.delete(movie_del)
            db.session.commit()
            return f"удален фильм id={uid}", 204
        except Exception as e:
            # db.session.rollback()
            return str(e), 404


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        result = db.session.query(Director).all()
        return directors_schema.dump(result), 200
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)

        return "", 201

@directors_ns.route('/<int:uid>')
class DirectorsView(Resource):
    def get(self, uid):
        try:
            result = db.session.query(Director).get(uid)
            return director_schema.dump(result), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        """
        обновляет данные фильма
        :param uid:
        :return:
        """
        try:
            director = db.session.query(Director).get(uid)
            director_req = request.json
            director.name = director_req.get("name")
            db.session.add(director)
            db.session.commit()
            return "", 204
        except Exception as e:
            db.session.rollback()
            return str(e), 404

    def delete(self, uid):
        """
        удаляет режисера
        :param uid:
        :return:
        """
        try:
            director_del = db.session.query(Director).get(uid)
            db.session.delete(director_del)
            db.session.commit()
            return f"удален режисер с id={uid}", 204
        except Exception as e:
            db.session.rollback()
            return str(e), 404


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        result = db.session.query(Genre).all()
        return genres_schema.dump(result), 200
    def post(self):
        req_genre = request.json
        new_genre = Genre(**req_genre)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genres_ns.route('/<int:uid>')
class GenresView(Resource):
    def get(self, uid):
        try:
            result = db.session.query(Genre).get(uid)
            return genre_schema.dump(result), 200
        except Exception as e:
            return str(e), 404
    def put(self, uid):
        """
        обновляет данные жанра
        :param uid:
        :return:
        """
        try:
            genre = db.session.query(Genre).get(uid)
            genre_req = request.json
            genre.name = genre_req.get("name")
            db.session.add(genre)
            db.session.commit()
            return "обновлен жанр", 204
        except Exception as e:
            db.session.rollback()
            return str(e), 404

    def delete(self, uid):
        """
        удаляет жанр
        :param uid:
        :return:
        """
        try:
            genre_del = db.session.query(Genre).get(uid)
            db.session.delete(genre_del)
            db.session.commit()
            return f"удален жанр с id={uid}", 204
        except Exception as e:
            db.session.rollback()
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
