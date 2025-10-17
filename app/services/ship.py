from sqlalchemy.orm import Session
from app.models.ship import Ship
from app.models.user import User
from app.schemas.ship import ShipStatus, Position

def get_all_ships(db: Session):
    ships = db.query(Ship).all()
    result = []
    for ship in ships:
        user = db.query(User).filter(User.id == ship.owner_id).first()
        username = user.username if user else "unknown"
        current_pos = Position(x=ship.current_pos_x, y=ship.current_pos_y)
        start_pos = Position(x=ship.start_pos_x, y=ship.start_pos_y) if ship.start_pos_x is not None and ship.start_pos_y is not None else None
        end_pos = Position(x=ship.end_pos_x, y=ship.end_pos_y) if ship.end_pos_x is not None and ship.end_pos_y is not None else None
        result.append(
            ShipStatus(
                username=username,
                isMoving=ship.is_moving,
                currentPosition=current_pos,
                startPosition=start_pos,
                endPosition=end_pos
            )
        )
    return result