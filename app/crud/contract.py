from app.models.models import Contract, Customer, Employee

def create_contract(session, data):
    try:
        new_contract = Contract(**data)
        session.add(new_contract)
        session.commit()
        session.refresh(new_contract)
        return new_contract
    except Exception as e:
        raise ValueError(f"Erreur lors de la création du contrat : {e}")

def get_all_contracts(session):
    return session.query(Contract).all()

def get_contracts_by(session, attribute, value):
    if not hasattr(Contract, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Contract.")
    
    if value.lower() in ("none", "null"):
        return session.query(Contract).filter(getattr(Contract, attribute).is_(None)).all()
    else:
        return session.query(Contract).filter(getattr(Contract, attribute) == value).all()

def update_contract_by_id(session, contract_id, attribute, value, employee_number):
    
    if not hasattr(Contract, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Contract.")
    
    if attribute not in ['customer_id', 'sale_contact_id', 'total_amount', 'remaining_amount', 'signed']:
        raise ValueError(f"L'attribut '{attribute}' ne peut pas être mis à jour directement.")

    contract = session.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise ValueError(f"Aucun contrat trouvé avec l'ID {contract_id}.")
    
    if contract.employee.employee_number != employee_number:
        raise ValueError(f"Vous n'êtes pas le commercial associé au contrat.")

    match attribute:
        case "customer_id":
            if not session.query(Customer).filter(Customer.id == value).first():
                raise ValueError(f"Aucun client trouvé avec l'ID {value}.")

        case "sale_contact_id":
            sale_contact = session.query(Employee).filter(Employee.id == value).first()
            if not sale_contact:
                raise ValueError(f"Aucun employé trouvé avec l'ID {value}.")

            if sale_contact.role.name != "Commercial":
                raise ValueError(f"L'employé avec l'ID {value} n'est pas un commercial.")
            
        case "total_amount":
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f"Le montant total doit être un nombre.")
            
            if value < 0:
                raise ValueError(f"Le montant total ne peut pas être négatif.")

        case "remaining_amount":
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f"Le montant total doit être un nombre.")
            
            if value < 0:
                raise ValueError(f"Le montant restant ne peut pas être négatif.")
            
            if value > contract.total_amount:
                raise ValueError(f"Le montant restant ne peut pas être supérieur au montant total.")
        
        case "signed":
            if value in ["oui", "o", "yes", "y", "1", "true"]:
                value = True
            elif value in ["non", "n", "no", "0", "false"]:
                value = False
            else:
                raise ValueError(f"La valeur de l'attribut 'signed' doit être 'oui' ou 'non'.")
    
    setattr(contract, attribute, value)
    session.commit()
    session.refresh(contract)
    return contract

def delete_contract_by_id(session, contract_id):
    contract = session.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise ValueError(f"Aucun contrat trouvé avec l'ID {contract_id}.")
    
    session.delete(contract)
    session.commit()
    return contract