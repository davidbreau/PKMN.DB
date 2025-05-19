from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Session
from sqlalchemy import Float
import polars as pl
from pathlib import Path

if TYPE_CHECKING:
    from .GO_type import GO_Type

class GO_TypeEffectiveness(SQLModel, table=True):
    __tablename__ = "go_types_effectiveness"
    
    # COLUMNS
    id: int | None = Field(default=None, primary_key=True)
    attacking_type_id: int = Field(foreign_key="go_types.id")
    defending_type_id: int = Field(foreign_key="go_types.id")
    effectiveness: float = Field(sa_type=Float(precision=2, asdecimal=False))
    
    # RELATIONSHIPS
    attacking_type_id___GO_Type__id: "GO_Type" = Relationship(
        back_populates="id___GO_TypeEffectiveness__attacking_type_id",
        sa_relationship_kwargs={"foreign_keys": "[GO_TypeEffectiveness.attacking_type_id]"}
    )
    defending_type_id___GO_Type__id: "GO_Type" = Relationship(
        back_populates="id___GO_TypeEffectiveness__defending_type_id",
        sa_relationship_kwargs={"foreign_keys": "[GO_TypeEffectiveness.defending_type_id]"}
    )
    
    @staticmethod
    def initialize_type_effectiveness(session: Session) -> None:
        """Initialize type effectiveness data from the Excel file."""
        excel_path = Path('data/pokemon_go_type_effectiveness_chart.xlsx')
        
        # Read Excel file with polars
        df = pl.read_excel(excel_path)
        
        # Get type names from columns (excluding 'Attacking Type' column)
        type_names = [col for col in df.columns if col != "Attacking Type"]
        
        # Create type ID mapping based on position in columns (1-based index)
        type_id_mapping = {type_name: idx + 1 for idx, type_name in enumerate(type_names)}
        
        # For each row in DataFrame
        for attacking_type in type_names:
            attacking_id = type_id_mapping[attacking_type]
            
            # For each defending type
            for defending_type in type_names:
                defending_id = type_id_mapping[defending_type]
                
                # Get effectiveness value
                effectiveness = df.filter(pl.col("Attacking Type") == attacking_type).select(defending_type).item()
                
                # Create database entry
                type_effectiveness = GO_TypeEffectiveness(
                    attacking_type_id=attacking_id,
                    defending_type_id=defending_id,
                    effectiveness=float(effectiveness)
                )
                session.add(type_effectiveness)
        
        session.commit() 