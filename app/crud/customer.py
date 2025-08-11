from app.models.models import Customer, Employee

def create_customer(session, data):
    try:
        new_customer = Customer(**data)
        session.add(new_customer)
        session.commit()
        session.refresh(new_customer)
        return new_customer
    except Exception as e:
        raise ValueError(f"Erreur lors de la création du client : {e}")

def get_all_customers(session):
    return session.query(Customer).all()

def get_customers_by(session, attribute, value):
    if not hasattr(Customer, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Customer.")

    return session.query(Customer).filter(getattr(Customer, attribute) == value).all()

def update_customer_by_id(session, customer_id, attribute, value):
    if not hasattr(Customer, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Customer.")
    
    if attribute == "sale_contact":
        raise ValueError(f"L'attribut 'sale_contact' ne peut être mis à jour que par le département gestion.")
    
    if attribute not in ['first_name', 'last_name', 'email', 'phone', 'company']:
        raise ValueError(f"L'attribut '{attribute}' ne peut pas être mis à jour directement.")
    
    customer = session.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise ValueError(f"Aucun client trouvé avec l'ID {customer_id}.")
    
    setattr(customer, attribute, value)
    session.commit()
    session.refresh(customer)
    return customer

def update_customer_sale_contact(session, customer_id, sale_contact_number):
    sale_contact = session.query(Employee).filter(Employee.employee_number == sale_contact_number).first()
    
    if not sale_contact:
        raise ValueError(f"Aucun employé trouvé avec le numéro {sale_contact_number}.")

    if sale_contact.role.name != "Commercial":
        raise ValueError(f"L'employé {sale_contact_number} n'est pas un commercial.")
    
    customer = session.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise ValueError(f"Aucun client trouvé avec l'ID {customer_id}.")

    customer.sale_contact_id = sale_contact.id
    session.commit()
    session.refresh(customer)
    return customer