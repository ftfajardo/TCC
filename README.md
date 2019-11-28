
# Detection and regonition - TG



## Getting Started

git clone --depth=1 https://github.com/ftfajardo/mysite.git

### Prerequisites

Images inside a date file and with times in their name;

example:
```
media/dias/10-10-10/10:00:00.jpg
media/dias/10-10-10/10:50:00.jpg
media/dias/10-10-10/10:60:00.jpg
```
OR

media/dias/10-10-10/eminem.png

but check the option that uses image modification time otherwise will fail.



## Running with docker

docker-compose up -d

docker-compose exec web python manage.py makemigrations

docker-compose exec web python manage.py migrate

## Sets Links

http://www-prima.inrialpes.fr/Pointing04/data-face.html

http://vision.ucsd.edu/~leekc/ExtYaleDatabase/ExtYaleB.html

http://www.consortium.ri.cmu.edu/data/SRD/release/

For my dataset email-me ftfajardo@gmail.com

## Authors

* **Francisco Tassinari Fajardo** 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

