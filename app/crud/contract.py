from app.models.models import Contract, Employee


def create_contract(session, data):
    """Crée un nouveau contrat."""
    try:
        new_contract = Contract(**data)
        session.add(new_contract)
        session.commit()
        session.refresh(new_contract)
        return new_contract
    except Exception as e:
        raise ValueError(f"Erreur lors de la création du contrat : {e}")


def get_contracts(session, filters={}, sorts={}):
    """Récupère la liste des contrats en fonction des critères du filtrage et du tri."""
    query = session.query(Contract)

    for attr, value in filters.items():
        if not hasattr(Contract, attr):
            raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Contract.")

        column = getattr(Contract, attr)

        if value.lower() in ("none", "null"):
            query = query.filter(column.is_(None))
            continue

        if value.lower() in ("true", "false"):
            query = query.filter(column.is_(value.lower() == "true"))
            continue

        query = query.filter(column.contains(value))

    if sorts:
        for attr, order in sorts.items():
            if not hasattr(Contract, attr):
                raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Contract.")

            column = getattr(Contract, attr)

            if order == "asc":
                query = query.order_by(column.asc())
            elif order == "desc":
                query = query.order_by(column.desc())

    return query.all()


def update_contract(session, contract_id, updates, req_emp_num):
    """Met à jour un contrat."""
    contract = session.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise ValueError(f"Aucun contrat trouvé avec l'ID {contract_id}.")

    employee = session.query(Employee).filter(Employee.employee_number == req_emp_num).first()

    if contract.sale_contact:
        if contract.sale_contact.employee_number != req_emp_num and employee.role.name != "Management":
            raise ValueError("Vous n'êtes pas autorisé à modifier ce contrat.")
    else:
        if employee.role.name != "Management":
            raise ValueError("Seul un manager peut modifier le contrat s'il n'a pas de commercial associé.")

    for attribute, value in updates.items():
        if not hasattr(Contract, attribute):
            raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Contract.")

        match attribute:
            case "total_amount":
                try:
                    value = float(value)
                except ValueError:
                    raise ValueError("Le montant total doit être un nombre.")

                if value < 0:
                    raise ValueError("Le montant total ne peut pas être négatif.")

            case "remaining_amount":
                try:
                    value = float(value)
                except ValueError:
                    raise ValueError("Le montant total doit être un nombre.")

                if value < 0:
                    raise ValueError("Le montant restant ne peut pas être négatif.")

                if value > contract.total_amount:
                    raise ValueError("Le montant restant ne peut pas être supérieur au montant total.")

            case "signed":
                if value.lower() in ["oui", "o", "yes", "y", "1", "true"]:
                    value = True
                elif value.lower() in ["non", "n", "no", "0", "false"]:
                    if contract.event:
                        raise ValueError("Le contrat est lié à un événement " /
                                         "et ne peut pas être marqué comme non signé.")
                    value = False
                else:
                    raise ValueError("La valeur de l'attribut 'signed' doit être 'True' ou 'False'.")

            case _:
                raise ValueError(f"L'attribut '{attribute}' ne peut pas être mis à jour directement.")

        setattr(contract, attribute, value)

    session.commit()
    session.refresh(contract)
    return contract


def delete_contract(session, contract):
    """Supprime un contrat."""
    session.delete(contract)
    session.commit()
