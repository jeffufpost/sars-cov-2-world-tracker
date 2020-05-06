import dash_bootstrap_components as dbc


def Navbar():
     navbar = dbc.NavbarSimple(
           children=[
              dbc.NavItem(dbc.NavLink("French department tracker", href="/france")),
              dbc.DropdownMenu(
                 nav=True,
                 in_navbar=True,
                 label="Menu",
                 children=[
                    dbc.DropdownMenuItem(dbc.NavLink("More info", href="https://github.com/jeffufpost/sars-cov-2-world-tracker"))
                          ],
                      ),
                    ],
          brand="World tracker",
          brand_href="/world",
          sticky="top",
        )
     return navbar