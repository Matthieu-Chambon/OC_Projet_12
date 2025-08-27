from rich.console import Console
from rich.table import Table
from rich.text import Text

def display_roles(roles):
    table = Table(title="\n:lock: Liste des rôles :")
    table.title_style = "bold"

    table.add_column("id", justify="center", style="red")
    table.add_column("name", justify="left", style="cyan")
    table.add_column("description", justify="left", style="yellow")

    for role in roles:
        table.add_row(
            str(role.id),
            role.name,
            role.description if role.description else "None"
        )

    console = Console()
    console.print(table)
    console.print("\n")

def display_employees(employees, context):
    console = Console()
    
    if not employees:
        console.print(Text("\nAucun employé trouvé.", style="bold red"))
        return

    if context == "create":
        table = Table(title="\n:heavy_plus_sign: Nouvel employé créé :")
    elif context == "list":
        table = Table(title="\n:man: :woman: Liste des employés :")
    elif context == "update":
        table = Table(title="\n:pencil2:  Employé mis à jour :")
    elif context == "delete":
        table = Table(title="\n:heavy_minus_sign: Employé supprimé :")

    table.title_style = "bold"

    table.add_column("id", justify="center", style="red")
    table.add_column("employee_number", justify="center", style="green")
    table.add_column("first_name", justify="left", style="cyan")
    table.add_column("last_name", justify="left", style="cyan")
    table.add_column("email", justify="left", style="yellow")
    table.add_column("role_id", justify="left", style="magenta1")
    table.add_column("created_at", justify="left", style="")

    for employee in employees:
        table.add_row(
            str(employee.id),
            employee.employee_number,
            employee.first_name,
            employee.last_name,
            employee.email,
            f"{str(employee.role_id)} ({employee.role.name})",
            employee.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )

    table.caption = f"{len(employees)} résultat(s)"
    table.caption_style = "italic white"
    table.caption_justify = "right"

    console.print(table)
    console.print("\n")

def display_customers(customers, context):
    console = Console()

    if not customers:
        console.print(Text("Aucun client trouvé.", style="bold red"))
        return
   
    if context == "create":
        table = Table(title="\n:heavy_plus_sign: Nouveau client créé :")
    elif context == "list":
        table = Table(title="\n:man_office_worker: Liste des clients :")
    elif context == "update":
        table = Table(title="\n:pencil2:  Client mis à jour :")
    elif context == "delete":
        table = Table(title="\n:heavy_minus_sign: Client supprimé :")

    table.title_style = "bold"

    table.add_column("id", justify="center", style="red")
    table.add_column("first_name", justify="left", style="cyan")
    table.add_column("last_name", justify="left", style="cyan")
    table.add_column("email", justify="left", style="yellow")
    table.add_column("phone", justify="left", style="cyan1")
    table.add_column("company", justify="left", style="green")
    table.add_column("sale_contact_id", justify="left", style="magenta1")
    table.add_column("created_at", justify="left", style="")
    table.add_column("updated_at", justify="left", style="")

    for customer in customers:
        sc = customer.sale_contact
        
        if sc is not None:
            sale_contact_id = f"{str(customer.sale_contact_id)} ({sc.first_name} {sc.last_name} - {sc.employee_number})"
        else:
            sale_contact_id = "None"

        table.add_row(
            str(customer.id),
            customer.first_name,
            customer.last_name,
            customer.email,
            customer.phone if customer.phone else "None",
            customer.company if customer.company else "None",
            sale_contact_id,
            customer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            customer.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    table.caption = f"{len(customers)} résultat(s)"
    table.caption_style = "italic white"
    table.caption_justify = "right"

    console.print(table)
    console.print("\n")
    
def display_contracts(contracts, context):
    console = Console()

    if not contracts:
        console.print(Text("Aucun contrat trouvé.", style="bold red"))
        return
    
    if context == "create":
        table = Table(title="\n:heavy_plus_sign: Nouveau contrat créé :")
    elif context == "list":
        table = Table(title="\n:page_facing_up: Liste des contrats :")
    elif context == "update":
        table = Table(title="\n:pencil2:  Contrat mis à jour :")
    elif context == "delete":
        table = Table(title="\n:heavy_minus_sign: Contrat supprimé :")

    
    table.title_style = "bold"

    table.add_column("id", justify="center", style="red")
    table.add_column("customer_id", justify="left", style="green")
    table.add_column("sale_contact_id", justify="left", style="magenta1")
    table.add_column("total_amount (en €)", justify="right", style="yellow")
    table.add_column("remaining_amount (en €)", justify="right", style="yellow")
    table.add_column("signed", justify="left", style="cyan")
    table.add_column("created_at", justify="left", style="")

    for contract in contracts:
        cu = contract.customer
        sc = contract.sale_contact
        
        if sc is not None:
            sale_contact_id = f"{str(contract.sale_contact_id)} ({sc.first_name} {sc.last_name} - {sc.employee_number})"
        else:
            sale_contact_id = "None"

        table.add_row(
            str(contract.id),
            f"{str(contract.customer_id)} ({cu.first_name} {cu.last_name})",
            sale_contact_id,
            str(contract.total_amount),
            str(contract.remaining_amount),
            str(contract.signed),
            contract.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )

    table.caption = f"{len(contracts)} résultat(s)"
    table.caption_style = "italic white"
    table.caption_justify = "right"

    console.print(table)
    console.print("\n")

def display_events(events, context):
    console = Console()

    if not events:
        console.print(Text("Aucun événement trouvé.", style="bold red"))
        return
    
    if context == "create":
        table = Table(title="\n:heavy_plus_sign: Nouvel événement créé :")
    elif context == "list":
        table = Table(title="\n:calendar: Liste des événements :")
    elif context == "update":
        table = Table(title="\n:pencil2:  Événement mis à jour :")
    elif context == "delete":
        table = Table(title="\n:heavy_minus_sign: Événement supprimé :")

    table.title_style = "bold"

    table.add_column("id", justify="center", style="red")
    table.add_column("name", justify="left", style="cyan")
    table.add_column("contract_id", justify="left", style="green")
    table.add_column("support_contact_id", justify="left", style="magenta1")
    table.add_column("start_date", justify="left", style="yellow")
    table.add_column("end_date", justify="left", style="yellow")
    table.add_column("location", justify="left", style="bright_green")
    table.add_column("attendees", justify="right", style="cyan1")
    table.add_column("notes", justify="left", style="dark_orange")
    table.add_column("created_at", justify="left", style="")

    for event in events:
        cust = event.contract.customer
        event_contract_id = f"{str(event.contract_id)} ({cust.first_name} {cust.last_name})"

        sc = event.support_contact

        if sc is not None:
            support_contact_id = f"{str(event.support_contact_id)} ({sc.first_name} {sc.last_name} - {sc.employee_number})"
        else:
            support_contact_id = "None"

        table.add_row(
            str(event.id),
            event.name,
            event_contract_id,
            support_contact_id,
            event.start_date.strftime("%Y-%m-%d %H:%M:%S") if event.start_date else "None",
            event.end_date.strftime("%Y-%m-%d %H:%M:%S") if event.end_date else "None",
            event.location if event.location else "None",
            str(event.attendees) if event.attendees else "None",
            event.notes if event.notes else "None",
            event.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )

    table.caption = f"{len(events)} résultat(s)"
    table.caption_style = "italic white"
    table.caption_justify = "right"

    console.print(table)
    console.print("\n")