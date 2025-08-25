from sqlalchemy import Integer, String, Enum, Text, ForeignKey, DECIMAL, TIMESTAMP, DateTime, Boolean, func
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column


Base = declarative_base()

class Role(Base):
    __tablename__ = "role"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', description='{self.description}')>"


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    created_at: Mapped[DateTime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    role = relationship("Role", back_populates="employees")
    customers: Mapped[list["Customer"]] = relationship("Customer", back_populates="sale_contact", passive_deletes=True)
    contracts : Mapped[list["Contract"]] = relationship("Contract", back_populates="sale_contact", passive_deletes=True)
    events: Mapped[list["Event"]] = relationship("Event", back_populates="support_contact", passive_deletes=True)

    def __repr__(self):
        return f"<Employee(id={self.id}, employee_number='{self.employee_number}', first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}', role_id={self.role_id})>"
        

class Customer(Base):
    __tablename__ = "customer"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    company: Mapped[str] = mapped_column(String(100), nullable=True)
    sale_contact_id: Mapped[int] = mapped_column(ForeignKey("employee.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    sale_contact = relationship("Employee", back_populates="customers")
    contracts : Mapped[list["Contract"]] = relationship("Contract", back_populates="customer", passive_deletes=True)

    def __repr__(self):
        return f"<Customer(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}', phone='{self.phone}', company='{self.company}', sale_contact_id='{self.sale_contact_id}')>"


class Contract(Base):
    __tablename__ = "contract"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id", ondelete="CASCADE"), nullable=False)
    sale_contact_id: Mapped[int] = mapped_column(ForeignKey("employee.id", ondelete="SET NULL"), nullable=True)
    total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    remaining_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    signed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)    

    customer = relationship("Customer", back_populates="contracts")
    sale_contact = relationship("Employee", back_populates="contracts")
    event = relationship("Event", back_populates="contract", uselist=False, passive_deletes=True)
    
    def __repr__(self):
        return f"<Contract(id={self.id}, customer_id={self.customer_id}, sale_contact_id={self.sale_contact_id}, total_amount={self.total_amount}, remaining_amount={self.remaining_amount}, signed={self.signed})>"
    
    
class Event(Base):
    __tablename__ = "event"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id", ondelete="CASCADE"), nullable=False)
    support_contact_id: Mapped[int] = mapped_column(ForeignKey("employee.id", ondelete="SET NULL"), nullable=True)
    start_date: Mapped[DateTime] = mapped_column(TIMESTAMP, nullable=True)
    end_date: Mapped[DateTime] = mapped_column(TIMESTAMP, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    attendees: Mapped[int] = mapped_column(Integer, nullable=True)
    note: Mapped[str] = mapped_column(Text(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    contract = relationship("Contract", back_populates="event")
    support_contact = relationship("Employee", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', contract_id={self.contract_id}, support_contact_id={self.support_contact_id}, start_date='{self.start_date}', end_date='{self.end_date}', location='{self.location}', attendees={self.attendees}, note='{self.note}')>"
