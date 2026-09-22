# Book API Project
This project is for me to continue to practice foundational coding principles, as well as continue to learn and grow my skills as a programmer. This is a Book API project that will function as a virtual library that shows what books you have. 

This project uses Python and FastAPI. No AI used to build the code, to continue to strengthen my knowledge and muscle memory of coding. Enjoy :)

9/22/26 - I am adding multiple databases so I can practice micro transactions and eventually a kubernetes system
        - using book backend as a cache system rather than an inventory system to help the app speed up. then, it will call either google books api or open library books api if the title doesn't exist in the cache, then store the recent book and delete oldest one
        - This method would also call book ISBN from user info in backend to the book cache