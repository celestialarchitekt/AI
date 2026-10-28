"""
fastAPI - request model
"""

from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name:str
    description:str 
    price:float
    

app = FastAPI()


@app.post("/items")
async def create_items(item:Item):
    
    #item is pydantic object of class Item, model_dump() converts it into a dictionary
    item_dict = item.model_dump()

    item.price+=100
    new_price=item.price
    
    #update the dictionary and add a new 'key'
    item_dict.update({"new_price":new_price})
   
    return f"item dictionary {item_dict}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)