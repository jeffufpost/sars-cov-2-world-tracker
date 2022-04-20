import dash_bootstrap_components as dbc


def Navbar():
     navbar = dbc.NavbarSimple(
           children=[
              dbc.NavItem(dbc.NavLink("France tracker", href="/france")),
              dbc.DropdownMenu(
                 nav=True,
                 in_navbar=True,
                 label="Menu",
                 children=[
                    dbc.DropdownMenuItem(dbc.NavLink("Github", href="https://github.com/jeffufpost/sars-cov-2-world-tracker")),
                    dbc.DropdownMenuItem(dbc.NavLink("Blog", href="https://jeffreypost.dev/scattered-thoughts"))
                          ],
                      ),
                    ],
          brand="World tracker",
          brand_href="/world",
          sticky="top",
        )
     return navbar
