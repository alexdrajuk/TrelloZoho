# import re
import settings
import utils

def foo(**kwargs):
    print(kwargs.get('name'))
    
# foo(name='Alex')


a = {
    'name': 'Alex',
    'age': 30,
}

print(a.keys())
print('name' in a.keys())
