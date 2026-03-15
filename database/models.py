from typing import List
from sqlalchemy import ForeignKey, create_engine, UniqueConstraint, DateTime, Enum, insert
from sqlalchemy.orm import DeclarativeBase, declarative_mixin, Mapped, mapped_column, relationship, Session
from sqlalchemy.sql import func
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import enum
load_dotenv()

engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)

class Base(DeclarativeBase):
    pass

class UrlStatus(enum.Enum):
    open = "open"
    processing = "processing"
    done = "done"
    failed = "failed"

class SearchParams(Base):
    __tablename__ = "search_params"
    id: Mapped[int] = mapped_column(primary_key=True)
    country: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    zip_code: Mapped[str] = mapped_column(nullable=True)
    estate_type: Mapped[str] = mapped_column(nullable=False)
    rent_or_buy: Mapped[str] = mapped_column(nullable=False)
    listing_count: Mapped[int] = mapped_column(nullable=False)
    page: Mapped[int] = mapped_column(nullable=False)
    last_used: Mapped[datetime|None] = mapped_column(DateTime, nullable=True)

class UrlQueue(Base):
    __tablename__ = "url_queue"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    status: Mapped[UrlStatus] = mapped_column(Enum(UrlStatus, name="url_status"), nullable=False)
    claimed_by: Mapped[int | None] = mapped_column(nullable=True)
    claimed_at: Mapped[datetime|None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class Agency(Base):
    __tablename__ = "agency"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    rating: Mapped[float] = mapped_column(nullable=True)
    homepage: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    houses: Mapped[List["House"]] = relationship(back_populates="agency")
    apartments: Mapped[List["Apartment"]] = relationship(back_populates="agency")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, rating={self.rating}, homepage={self.homepage}, address={self.address})"
        
@declarative_mixin
class RealEstate:
    title: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    estate_type: Mapped[str] = mapped_column(nullable=True)
    listing_type: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[str] = mapped_column(nullable=True)
    price_m2: Mapped[str] = mapped_column(nullable=True)
    rent_cold: Mapped[str] = mapped_column(nullable=True)
    rent_complete: Mapped[str] = mapped_column(nullable=True)
    house_money: Mapped[str] = mapped_column(nullable=True)
    rent_extra_costs: Mapped[str] = mapped_column(nullable=True)
    rent_heating_costs: Mapped[str] = mapped_column(nullable=True)
    rent_deposit: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    zip_code: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    rooms: Mapped[float] = mapped_column(nullable=True)
    sleeping_rooms: Mapped[int] = mapped_column(nullable=True)
    bathrooms: Mapped[int] = mapped_column(nullable=True)
    floor: Mapped[str] = mapped_column(nullable=True)
    living_space: Mapped[str] = mapped_column(nullable=True)
    garage_parking_slots: Mapped[int] = mapped_column(nullable=True)
    lift: Mapped[bool] = mapped_column(nullable=True)
    barrier_free: Mapped[bool] = mapped_column(nullable=True)
    garden: Mapped[bool] = mapped_column(nullable=True)
    internet_speed_telekom: Mapped[str] = mapped_column(nullable=True)
    fitted_kitchen: Mapped[bool] = mapped_column(nullable=True)
    basement: Mapped[bool] = mapped_column(nullable=True)
    rented: Mapped[bool] = mapped_column(nullable=True)
    available_from: Mapped[str] = mapped_column(nullable=True)
    provision: Mapped[str] = mapped_column(nullable=True)
    rent_income: Mapped[str] = mapped_column(nullable=True)
    incidental_purchase_costs: Mapped[str] = mapped_column(nullable=True)
    property_acquisition_tax: Mapped[str] = mapped_column(nullable=True)
    brokerage_commission: Mapped[str] = mapped_column(nullable=True)
    notary_fees: Mapped[str] = mapped_column(nullable=True)
    land_registry_entry: Mapped[str] = mapped_column(nullable=True)
    building_year: Mapped[str] = mapped_column(nullable=True)
    estate_condition: Mapped[str] = mapped_column(nullable=True)
    interior_quality: Mapped[str] = mapped_column(nullable=True)
    heating_type: Mapped[str] = mapped_column(nullable=True)
    energy_performance_certificate_type: Mapped[str] = mapped_column(nullable=True)
    energy_source: Mapped[str] = mapped_column(nullable=True)
    energy_demand: Mapped[str] = mapped_column(nullable=True)
    energy_efficiency_class: Mapped[str] = mapped_column(nullable=True)
    general_description: Mapped[str] = mapped_column(nullable=True)
    object_description: Mapped[str] = mapped_column(nullable=True)
    place_description: Mapped[str] = mapped_column(nullable=True)
    other_description: Mapped[str] = mapped_column(nullable=True)
    total_costs: Mapped[float] = mapped_column(nullable=True)
    agency_id: Mapped[int] = mapped_column(ForeignKey("agency.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title={self.title}, price={self.price}, url={self.url})"

    def calculate_incidental_purchase_costs(self) -> float:
        if self.incidental_purchase_costs is not None and '%' in self.incidental_purchase_costs:
            incidental_purchase_costs_num = self.incidental_purchase_costs.split(" ")[0]
            incidental_purchase_costs_float = float(incidental_purchase_costs_num)/100
            return incidental_purchase_costs_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_property_acquisition_tax(self) -> float:
        if self.property_acquisition_tax is not None and '%' in self.property_acquisition_tax:
            property_acquisition_tax_num = self.property_acquisition_tax.split(" ")[0]
            property_acquisition_tax_float = float(property_acquisition_tax_num)/100
            return property_acquisition_tax_float
        else:
            raise Exception("No Percent Sign in String")
    
    
    def calculate_brokerage_commission(self) -> float:
        if self.brokerage_commission is not None and '%' in self.brokerage_commission:
            brokerage_commission_num = self.brokerage_commission.split(" ")[0]
            brokerage_commission_float = float(brokerage_commission_num)/100
            return brokerage_commission_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_notary_fees(self) -> float:
        if self.notary_fees is not None and '%' in self.notary_fees:
            notary_fees_num = self.notary_fees.split(" ")[0]
            notary_fees_float = float(notary_fees_num)/100
            return notary_fees_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_land_registry_entry(self) -> float:
        if self.land_registry_entry is not None and '%' in self.land_registry_entry:
            land_registry_entry_num = self.land_registry_entry.split(" ")[0]
            land_registry_entry_float = float(land_registry_entry_num)/100
            return land_registry_entry_float
        else:
            raise Exception("No Percent Sign in String")

class House(RealEstate, Base):
    __tablename__ = "houses"
    __table_args__ = (UniqueConstraint("url", "title", name="uq_houses_url_title"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    property_space: Mapped[str] = mapped_column(nullable=True)
    agency: Mapped[Agency | None] = relationship(back_populates="houses")
        
class Apartment(RealEstate, Base):
    __tablename__ = "apartments"
    __table_args__ = (UniqueConstraint("url", "title", name="uq_apartments_url_title"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    agency: Mapped[Agency | None] = relationship(back_populates="apartments")

        
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.execute(
            insert(SearchParams), 
            [
                {"country": "de", "state": "sachsen", "city": "leipzig", "estate_type": "apartment", "rent_or_buy": "buy", "listing_count": 50, "page": 1, "last_used": datetime.now() - timedelta(hours=1)},
                {"country": "de", "state": "sachsen", "city": "leipzig", "estate_type": "apartment", "rent_or_buy": "rent", "listing_count": 50, "page": 1, "last_used": datetime.now()- timedelta(hours=1)},
                {"country": "de", "state": "sachsen", "city": "leipzig", "estate_type": "house", "rent_or_buy": "buy", "listing_count": 50, "page": 1, "last_used": datetime.now()- timedelta(hours=1)},
                {"country": "de", "state": "sachsen", "city": "leipzig", "estate_type": "house", "rent_or_buy": "rent", "listing_count": 50, "page": 1, "last_used": datetime.now()- timedelta(hours=1)},
            ]
        )
        session.commit()