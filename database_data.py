from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="Ziko", email="ziko@gmail.com",
             picture='''https://pbs.twimg.com/profile_images/2671170543/
                     18debd694829ed78203a5a36dd364160_400x400.png''')
session.add(User1)
session.commit()

# Create categories data in DB

category1 = Category(name="Soccer", user_id=1)
session.add(category1)
session.commit()

category2 = Category(name="Basketball", user_id=1)
session.add(category2)
session.commit()

category3 = Category(name="Baseball", user_id=1)
session.add(category3)
session.commit()

category4 = Category(name="Frisebee", user_id=1)
session.add(category4)
session.commit()

category5 = Category(name="Snowboarding", user_id=1)
session.add(category5)
session.commit()

category6 = Category(name="Rock Climbing", user_id=1)
session.add(category6)
session.commit()

category7 = Category(name="Foosball", user_id=1)
session.add(category7)
session.commit()

category8 = Category(name="Skating", user_id=1)
session.add(category8)
session.commit()

category9 = Category(name="Hockey", user_id=1)
session.add(category9)
session.commit()

# Create items data in DB

item1 = Item(name="Soso", cat=category1, user_id=1,
             category="Soccer",
             description=("a bag ball game from Norway "
                           "in which the ball"))
session.add(item1)
session.commit()

item2 = Item(name="Sawsan", cat=category1, user_id=1,
             category="Soccer",
             description="""a variation of Ice Hockey.""")
session.add(item2)
session.commit()

item3 = Item(name="Baba", cat=category2, user_id=1,
             category="Basketball",
             description="""a type of Auto Racing""")
session.add(item3)
session.commit()

item4 = Item(name="Bosy", cat=category2, user_id=1,
             category="Basketball",
             description="""a trick shot competition""")
session.add(item4)
session.commit()

item5 = Item(name="Body", cat=category3, user_id=1,
             category="Baseball",
             description="""a variation of Rugby""")
session.add(item5)
session.commit()

item6 = Item(name="Bomba", cat=category3, user_id=1,
             category="Baseball",
             description="""a minified version of polo""")
session.add(item6)
session.commit()

item7 = Item(name="Fawzy", cat=category4, user_id=1,
             category="Frisebee",
             description="""a continuous race""")
session.add(item7)
session.commit()

item8 = Item(name="Fawzya", cat=category4, user_id=1,
             category="Frisebee",
             description="""water running competitions""")
session.add(item8)
session.commit()

item9 = Item(name="Goggles", cat=category5, user_id=1,
             category="Snowboarding",
             description="""a sport involving flying """)
session.add(item9)
session.commit()

item10 = Item(name="Snowboard", cat=category5, user_id=1,
              category="Snowboarding",
              description="""style of the martial art""")
session.add(item10)
session.commit()

item11 = Item(name="Rere", cat=category6, user_id=1,
              category="Rock Climbing",
              description="""activity using remotely .""")
session.add(item11)
session.commit()

item12 = Item(name="Roze", cat=category6, user_id=1,
              category="Rock Climbing",
              description="""team sport where a large group""")
session.add(item12)
session.commit()

item13 = Item(name="Fady", cat=category7, user_id=1,
              category="Foosball",
              description="""sport aerobatics involves aircraft.""")
session.add(item13)
session.commit()

item14 = Item(name="Faza", cat=category7, user_id=1,
              category="Foosball",
              description="""a freestyle skiing discipline""")
session.add(item14)
session.commit()

item15 = Item(name="Sameh", cat=category8, user_id=1,
              category="Skating",
              description="""an event combining two or more""")
session.add(item15)
session.commit()

item16 = Item(name="Smah", cat=category8, user_id=1,
              category="Skating",
              description="""thletes on snow skis perform""")
session.add(item16)
session.commit()

item17 = Item(name="Hesham", cat=category9, user_id=1,
              category="Hockey",
              description="""team of gymnasts work together""")
session.add(item17)
session.commit()

item18 = Item(name="Hanaa", cat=category9, user_id=1,
              category="Hockey",
              description="""commonly known as Downhill""")
session.add(item18)
session.commit()

print "added items!"
