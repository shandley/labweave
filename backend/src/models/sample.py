"""Sample model."""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Sample(BaseModel):
    """Sample model for tracking biological samples."""
    
    name = Column(String, nullable=False)
    sample_type = Column(String, nullable=False)  # soil, water, tissue, etc.
    barcode = Column(String, unique=True, index=True)
    status = Column(String, default="received")  # received, processing, processed, discarded
    
    # Metagenomics specific
    source = Column(String)  # Where the sample came from
    collection_date = Column(String)  # Will migrate to proper DateTime
    dna_concentration = Column(Float)
    quality_score = Column(Float)
    
    # Foreign keys
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    parent_sample_id = Column(Integer, ForeignKey("samples.id"))  # For derived samples
    
    # Relationships
    experiment = relationship("Experiment", back_populates="samples")
    parent_sample = relationship("Sample", remote_side="Sample.id")
    
    # Location tracking
    location = Column(String)  # Freezer, shelf, box position
    
    # Metadata
    metadata = Column(Text)  # JSON string for additional fields