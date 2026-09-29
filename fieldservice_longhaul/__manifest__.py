# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Long Hauling",
    "summary": "Enhancements for Long Hauling projects in Field Service management",
    "version": "14.0.1.3.0",
    "category": "Tools",
    "author": "Pakaispasi",
    "website": "https://github.com/OCA/field-service",
    "depends": ['base', 'fieldservice', 'fieldservice_route'],
    "data": [
        "views/menu.xml",
        "views/fsm_person.xml",
        "views/fsm_location.xml",
        "views/fsm_route.xml",
        "views/fsm_vehicle.xml",
        "views/fsm_driver_task.xml",
        "views/fsm_order.xml",
    ],
    'installable': True,
    "maintainers": ["gunakan"],
}
