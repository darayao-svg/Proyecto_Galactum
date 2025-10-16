from sqlalchemy.orm import Session
from app.models.ship import Ship
from app.schemas.ship import ShipStatus, Position

def get_all_ships(db: Session):
    ships = db.query(Ship).all()
    result = []
    for ship in ships:
        current_pos = Position(x=ship.current_x, y=ship.current_y)
        start_pos = Position(x=ship.start_x, y=ship.start_y) if ship.start_x and ship.start_y else None
        end_pos = Position(x=ship.end_x, y=ship.end_y) if ship.end_x and ship.end_y else None
        result.append(
            ShipStatus(
                username=ship.username,
                isMoving=ship.is_moving,
                currentPosition=current_pos,
                startPosition=start_pos,
                endPosition=end_pos
            )
        )
    return result