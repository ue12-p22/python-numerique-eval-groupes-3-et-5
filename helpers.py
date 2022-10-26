import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from inspect import signature
from itertools import cycle
from IPython.display import HTML, display

def test_table(f, tests):
    rows = [
        """<tr>
            <th style=\"text-align:center\">appel</th>
            <th style=\"text-align:center\">résultat</th>
            <th style=\"text-align:center\">attendu</th>
        </tr>"""
    ]

    num_errors = 0
    for args, expected in tests:
        actual = f(*args)
        colors = cycle(("blue", "green", "orange", "red"))
        formatted_args = ", ".join(f"<span style=\"font-weight: bold; color: {color}\">{arg!r:.30s}{'...' if len(repr(arg)) > 30 else ''}</span>" for arg, color in zip(args, colors))
        has_error = actual != expected
        cols = [
            f"<td style=\"font-family: monospace; text-align: center\"><span style=\"font-weight: bold\">{f.__name__}</span>({formatted_args})</td>",
            f"<td style=\"font-family: monospace; text-align: center;{'color: white' if has_error else ''}\">{repr(actual)}</td>",
            f"<td style=\"font-family: monospace; text-align: center\">{repr(expected)}</td>",
        ]
        rows.append(
            f"<tr style=\"{'background-color: red; color: white' if has_error else ''}\">{''.join(cols)}</tr>"
        )
        if has_error:
            num_errors += 1
    resultat = f"<p style=\"color: green; font-weight: bold\">Tous est bon 🥳</p>" if num_errors == 0 else f"<p style=\"color: red; font-weight: bold\">{num_errors} erreur{'s' if num_errors > 1 else ''} 😭</p>" 
    display(HTML(
       f"""<table><tr>{''.join(rows)}</tr></table>
       {resultat}
       """
    ))

def deplace_joueur_sequence(niveau, directions, deplace_joueur, arrivee=4):
        resultat = niveau.copy()

        kwargs = {}
        if len(signature(deplace_joueur).parameters) == 3:
            kwargs["masque_arrivee"] = niveau == arrivee
        
        for direction in directions:
            resultat = deplace_joueur(resultat, direction, **kwargs)
        return resultat

def test_solutions(*niveaux_et_sequences, locals):
    deplace_joueur = locals["deplace_joueur"]
    arrivee = locals.get("arrivee", 4)
    detecte_fin = locals["detecte_fin"]

    rows = [
        """<tr>
            <th style=\"text-align:center\">NIVEAU</th>
            <th style=\"text-align:center\">PARCOURS</th>
            <th style=\"text-align:center\">VALIDITÉ</th>
        </tr>"""
    ]
    for index_niveau, sequence in niveaux_et_sequences:
        niveau = levels[index_niveau]
        niveau_apres_deplacement = deplace_joueur_sequence(niveau=niveau, directions=sequence, deplace_joueur=deplace_joueur, arrivee=arrivee)
        
        cols = [
            f"<td style=\"text-align: center\">{index_niveau}</td>",
            
        ]
        if (len(sequence) > 0):
            cols.append(
                f"<td style=\"text-align: center\">{sequence:.10s}{'...' if len(sequence) > 10 else ''}</td>",
            )
        else:
            cols.append(
                f"<td style=\"text-align: center; font-style: italic\">TODO</td>",
            )
        if detecte_fin(niveau_apres_deplacement, niveau == arrivee):
            cols.append(
                f"<td style=\"text-align: center; color: white; background-color: green\">OK</td>",
            )
        else:
            cols.append(
                f"<td style=\"text-align: center; color: white; background-color: red\">KO</td>",
            )
        rows.append(
            f"<tr>{''.join(cols)}</tr>"
        )

    
    display(HTML(
       f"""<table><tr>{''.join(rows)}</tr></table>
       """
    ))

def affiche_sequences_joueur(*sequences, locals, niveau):
    affiche_niveau = locals.get("affiche_niveau")
    deplace_joueur = locals.get("deplace_joueur")
    arrivee = locals.get("arrivee", 4)

    fig, axs = plt.subplots(1, len(sequences), figsize=(len(sequences)*2, 4))

    if len(sequences) == 1:
        axs = [axs]
    for sequence, ax in  zip(sequences, axs):
        if len(sequence) == 0:
            ax.set_title("Position initiale", fontsize=8)
        else:
            char = '→' if len(sequence) <= 6 else ""
            ax.set_title(char.join([s[0].upper() for s in sequence]), fontsize=8)
        affiche_niveau(ax, deplace_joueur_sequence(niveau=niveau, directions=sequence, deplace_joueur=deplace_joueur, arrivee=arrivee))

def affiche_sequences_bloc(*sequences, locals, stating_bloc_position, niveau):
    affiche_niveau = locals.get("affiche_niveau")
    deplace_bloc = locals.get("deplace_bloc")

    fig, axs = plt.subplots(1, len(sequences))

    def deplace_bloc_sequence(directions):
        resultat = niveau.copy()
        x, y = stating_bloc_position
        for direction in directions:
            update = deplace_bloc(resultat, (x, y), direction)
            if update is not resultat:
                resultat = update
                if direction == "H":
                    x -= 1
                elif direction == "B":
                    x += 1
                elif direction == "G":
                    y -= 1
                elif direction == "D":
                    y += 1
        return resultat

    if len(sequences) == 1:
        axs = [axs]
    for sequence, ax in  zip(sequences, axs):
        if len(sequence) == 0:
            ax.set_title("Position initiale")
        else:
            char = '→' if len(sequences) <= 6 else ''
            ax.set_title(char.join([s[0].upper() for s in sequence]))
        affiche_niveau(ax, deplace_bloc_sequence(sequence))

direction_icone = {
    "G": "chevron-left",
    "D": "chevron-right",
    "H": "chevron-up",
    "B": "chevron-down",
}

def render_controls(niveau, *, locals, log_touches=False):
    affiche_niveau = locals["affiche_niveau"]
    deplace_joueur = locals["deplace_joueur"]
    detecte_fin = locals.get("detecte_fin", None)
    arrivee = locals.get("arrivee", 4)
    deja_fini = [False]

    niveau_temp = [niveau.copy()]
    num_args = len(signature(deplace_joueur).parameters)
    masque_arrivee = niveau == arrivee
    directions = [ "G", "B", "H", "D" ]

    fig, ax = plt.subplots()
    output = widgets.Output()

    def update_aff():
        with output:
            output.clear_output()
            affiche_niveau(ax, niveau_temp[0])
            display(fig)
            
    buttons = []
    for direction in directions:
        button = widgets.Button(icon=direction_icone[direction])
        buttons.append(button)

        def action(direction):
            def on_click(_v):
                if num_args == 2:
                    niveau_temp[0] = deplace_joueur(niveau_temp[0], direction)
                else:
                    niveau_temp[0] = deplace_joueur(niveau_temp[0], direction, masque_arrivee) 
                update_aff()
                fini = detecte_fin is not None and detecte_fin(niveau_temp[0], masque_arrivee)
                if log_touches and not deja_fini[0]:
                    print(direction, end='')
                if fini and not deja_fini[0]:
                    print("\nGAGNÉ 🎉🎉🎉")
                    deja_fini[0] = True
            return on_click
        button.on_click(action(direction))

    display(
        widgets.HBox(buttons),
        output
    )
    update_aff()

    plt.close()

## Actual levels, ripped from the sed version of the game
## 👁 https://aurelio.net/projects/sedsokoban/sokoban.sed.html
levels = [
    # level 0
    [
        [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,3,2,4,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0]
    ],

    # level 1
    [
        [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,0,0,2,0,2,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,0,1,0,1,1,0,1,0,0,0,1,1,1,1,1,1,0,0],
        [0,1,0,0,0,1,0,1,1,0,1,1,1,1,1,0,0,4,4,1,0,0],
        [0,1,0,2,0,0,2,0,0,0,0,0,0,0,0,0,0,4,4,1,0,0],
        [0,1,1,1,1,1,0,1,1,1,0,1,3,1,1,0,0,4,4,1,0,0],
        [0,0,0,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0],
        [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
    ],

    # level 2
    [
        [0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,1,0,2,0,0,2,0,0,1,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,1,2,1,1,1,1,0,0,1,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,0,0,3,0,1,1,0,0,1,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,1,0,1,0,0,2,0,1,1,0,0,0,0,0,0,0],
        [0,1,1,1,1,1,1,0,1,1,2,0,2,0,1,0,0,0,0,0,0,0],
        [0,0,0,1,0,2,0,0,2,0,2,0,2,0,1,0,0,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
    ],

    # level 3
    [
        [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,3,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,0,2,1,2,0,1,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,0,2,0,0,2,1,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,1,2,0,2,0,1,0,0,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,0,2,0,1,0,1,1,1,0,0,0,0],
        [0,1,4,4,4,4,0,0,1,1,0,2,0,0,2,0,0,1,0,0,0,0],
        [0,1,1,4,4,4,0,0,0,0,2,0,0,2,0,0,0,1,0,0,0,0],
        [0,1,4,4,4,4,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ],

    # level 4
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,4,4,4,4,1,0,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,4,4,4,4,1,0,0],
        [0,1,0,0,0,0,1,0,0,2,0,2,0,0,0,4,4,4,4,1,0,0],
        [0,1,0,2,2,2,1,2,0,0,2,0,1,0,0,4,4,4,4,1,0,0],
        [0,1,0,0,2,0,0,0,0,0,2,0,1,0,0,4,4,4,4,1,0,0],
        [0,1,0,2,2,0,1,2,0,2,0,2,1,1,1,1,1,1,1,1,0,0],
        [0,1,0,0,2,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,1,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,0,2,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,2,2,1,2,2,0,0,3,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
    ],

    # level 5
    [
        [0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,0,0,0,1,1,1,1,1,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,0,1,2,1,1,0,0,1,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,2,0,1,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,0,1,1,1,0,0,0,1,0,0,0,0],
        [0,1,4,4,4,4,0,0,1,1,0,2,0,0,2,1,1,1,0,0,0,0],
        [0,1,4,4,4,4,0,0,0,0,2,0,2,2,0,1,1,0,0,0,0,0],
        [0,1,4,4,4,4,0,0,1,1,2,0,0,2,0,3,1,0,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1,0,0,2,0,0,1,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,0,2,0,2,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],
    ],

    # level 6
    [
        [0,1,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,1,0,1,1,3,1,1,0,0,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,1,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,0,0,0,2,2,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,4,4,0,0,1,0,1,0,2,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,4,4,1,1,1,0,1,0,2,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,1,0,2,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,0,0,2,1,0,2,0,1,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,0,2,0,0,2,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
    ],

    # level 7
    [
        [0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
        [0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0],
        [0,1,1,0,1,0,3,1,1,0,2,2,0,1,0,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,2,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
        [0,1,0,0,2,0,0,1,1,1,0,0,0,1,0,0,0,0,0,0,0,0],
        [0,1,1,1,0,1,1,1,1,1,2,1,1,1,0,0,0,0,0,0,0,0],
        [0,1,0,2,0,0,1,1,1,0,4,4,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,2,0,2,0,2,0,4,4,4,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,1,1,1,4,4,4,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,2,2,0,1,0,1,4,4,4,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ],

    # level 8
    [
        [0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,2,0,0,0,2,0,2,0,1,0,0,0,0,0],
        [0,0,0,1,0,2,1,0,2,0,1,0,0,2,0,0,1,0,0,0,0,0],
        [0,0,0,1,0,0,2,0,2,0,0,1,0,0,0,0,1,0,0,0,0,0],
        [0,1,1,1,0,2,1,0,1,0,0,1,1,1,1,0,1,0,0,0,0,0],
        [0,1,3,1,2,0,2,0,2,0,0,1,1,0,0,0,1,0,0,0,0,0],
        [0,1,0,0,0,0,2,0,1,2,1,0,0,0,1,0,1,0,0,0,0,0],
        [0,1,0,0,0,2,0,0,0,0,2,0,2,0,2,0,1,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,4,4,4,4,4,4,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,4,4,4,4,4,4,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,4,4,4,4,4,4,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    ],

    # level 9
    [
        [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,4,4,4,1,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,1,1,1,0,0,4,4,4,1,0,0,0,0],
        [0,0,0,0,0,0,0,1,0,0,0,0,0,0,4,0,4,1,0,0,0,0],
        [0,0,0,0,0,0,0,1,0,0,1,1,0,0,4,4,4,1,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,0,1,1,0,0,4,4,4,1,0,0,0,0],
        [0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0],
        [0,0,0,0,0,0,1,0,2,2,2,0,1,1,0,0,0,0,0,0,0,0],
        [0,0,1,1,1,1,1,0,0,2,0,2,0,1,1,1,1,1,0,0,0,0],
        [0,1,1,0,0,0,1,2,0,2,0,0,0,1,0,0,0,1,0,0,0,0],
        [0,1,3,0,2,0,0,2,0,0,0,0,2,0,0,2,0,1,0,0,0,0],
        [0,1,1,1,1,1,1,0,2,2,0,2,0,1,1,1,1,1,0,0,0,0],
        [0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
    ],

    # level 10
    [
        [0,0,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
        [0,1,1,3,1,1,1,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0],
        [0,1,0,2,2,0,0,0,2,2,0,0,2,0,2,0,4,4,4,1,0,0],
        [0,1,0,0,2,2,2,1,0,0,0,0,2,0,0,1,4,4,4,1,0,0],
        [0,1,0,2,0,0,0,1,0,2,2,0,2,2,0,1,4,4,4,1,0,0],
        [0,1,1,1,0,0,0,1,0,0,2,0,0,0,0,1,4,4,4,1,0,0],
        [0,1,0,0,0,0,0,1,0,2,0,2,0,2,0,1,4,4,4,1,0,0],
        [0,1,0,0,0,0,1,1,1,1,1,1,0,1,1,1,4,4,4,1,0,0],
        [0,1,1,0,1,0,0,1,0,0,2,0,2,0,0,1,4,4,4,1,0,0],
        [0,1,0,0,1,1,0,1,0,2,2,0,2,0,2,1,1,4,4,1,0,0],
        [0,1,0,4,4,1,0,1,0,0,2,0,0,0,0,0,0,1,4,1,0,0],
        [0,1,0,4,4,1,0,1,0,2,2,2,0,2,2,2,0,1,4,1,0,0],
        [0,1,1,1,1,1,0,1,0,0,0,0,0,0,0,1,0,1,4,1,0,0],
        [0,0,0,0,0,1,0,1,1,1,1,1,1,1,1,1,0,1,4,1,0,0],
        [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,4,1,0,0],
        [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
    ],
]

levels = list(map(np.array, levels))