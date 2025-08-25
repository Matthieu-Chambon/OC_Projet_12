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
    
def get_customers(session, filters, sorts):
    query = session.query(Customer)

    for attr, value in filters.items():
        if not hasattr(Customer, attr):
            raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Customer.")
        
        column = getattr(Customer, attr)

        if value.lower() in ("none", "null"):
            query = query.filter(column.is_(None))
            continue
        
        if value.lower() in ("true", "false"):
            query = query.filter(column.is_(value.lower() == "true"))
            continue

        query = query.filter(column.contains(value))

    if sorts:
        for attr, order in sorts.items():
            if not hasattr(Customer, attr):
                raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Customer.")
            
            column = getattr(Customer, attr)
            
            if order == "asc":
                query = query.order_by(column.asc())
            elif order == "desc":
                query = query.order_by(column.desc())

    return query.all()

def update_customer(session, customer_id, updates, req_emp_num):
    customer = session.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise ValueError(f"Aucun client trouvé avec l'ID {customer_id}.")

    if customer.sale_contact.employee_number != req_emp_num:
        raise ValueError(f"Vous n'êtes pas le commercial associé à ce client.")

    for attribute, value in updates.items():
        if not hasattr(Customer, attribute):
            raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Customer.")

        if attribute == "sale_contact_id":
            raise ValueError(f"Veuillez utiliser la commande 'customer update-contact' pour mettre à jour le contact commercial.")

        if attribute not in ['first_name', 'last_name', 'email', 'phone', 'company']:
            raise ValueError(f"L'attribut '{attribute}' n'est pas modifiable.")

        setattr(customer, attribute, value)

    session.commit()
    session.refresh(customer)
    return customer

def update_customer_sale_contact(session, customer_id, sale_contact):
    employee = session.query(Employee).filter(
        (Employee.id == sale_contact) | (Employee.employee_number == sale_contact)
    ).first()

    if not employee:
        raise ValueError(f"Aucun employé trouvé avec le numéro ou l'ID {sale_contact}.")

    if employee.role.name != "Commercial":
        raise ValueError(f"L'employé {employee.first_name} {employee.last_name} ({employee.employee_number}) n'est pas un commercial.")

    customer = session.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise ValueError(f"Aucun client trouvé avec l'ID {customer_id}.")

    customer.sale_contact_id = employee.id
    session.commit()
    session.refresh(customer)

    for contrat in customer.contracts:
        contrat.sale_contact_id = employee.id
        session.commit()

    return customer

def delete_customer(session, customer):
    session.delete(customer)
    session.commit()
