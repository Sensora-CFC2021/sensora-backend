<img src="icon.png" />

## Backend API contents

- [Contents](#contents)
- [The problem](#the-problem)
- [Our solution](#our-solution)
- [Built with](#built-with)
- [About this repository](#about-this-repository)

### The problem

Climate change is affecting many sectors, and agriculture is definitely one of them. Due to the lack of knowledge, farmers are extensively using water, leading many developing countries to struggle with water depletion. Thus, it is crucial to educate farmers about using natural resources efficiently. However, the majority of the farmers worldwide are illiterate, making the process more complicated.


### Our solution

"Sensora" have many important features that will be one of the important steps of solving the problem addressed above. It can aggregate information about the soil moisture and temperature from the sensors installed in the field. Then, it will analyze the information and convey the result to the farmers in human voice. 


### About this repository

This repository contains the source code for API backend which is using Django REST framework work with sql database. 
Required versions 
```
Python 3.7 
pip 21.2
```

### STEP 1. Install requirements
``` commandline
pip install -r requirements.txt
```
### STEP 2. Migration

``` commandline
python manage.py migrate
```

### STEP 3. Run application

``` commandline
python manage.py runserver
```

Locate [localhost:8000](http://localhost:8000)

### Authors

- Ulziiburen Dorjpurev
- Erkhembayar Tsogtbaatar
- Itgel Delgerdalai
- Yesukhei Tumurbaatar
- Tsogtkhangai Munkhbayar
- Byambajargal Naranbat