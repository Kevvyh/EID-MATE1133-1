#=============================
#====IMPORTACION LIBRERIAS====
#=============================

import customtkinter as ctk
import matplotlib.pyplot as plt
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#================
#====INTERFAZ====
#================

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# vp = ventana principal
vp = ctk.CTk()
vp.title("Analizador y Visualizador de Límites")
vp.geometry("1200x700")

# la columna 0 se expande, fila 3 es donde va el grafico
vp.grid_columnconfigure(0, weight=1)
vp.grid_rowconfigure(3, weight=1)

# frame de arriba con los campos de entrada
marco_superior = ctk.CTkFrame(vp)
marco_superior.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

# campo donde el usuario escribe la funcion
campo_funcion = ctk.CTkEntry(marco_superior, placeholder_text="Función f(x)=")
campo_funcion.pack(side="left", padx=10, fill="x", expand=True)

# campo donde escribe el valor al que tiende x
campo_limite = ctk.CTkEntry(marco_superior, placeholder_text="h tiende a")
campo_limite.pack(side="left", padx=10)

boton_calcular = ctk.CTkButton(marco_superior, text="Calcular límite")
boton_calcular.pack(side="left", padx=10)

# donde se muestra el resultado del calculo
etiqueta_resultado = ctk.CTkLabel(vp, text="Resultado:", font=("Arial", 18))
etiqueta_resultado.grid(row=1, column=0)

# panel de ayuda con la sintaxis basica
texto_ayuda =   "  SINTAXIS:  Multiplicar -> 3*x  |  Dividir -> x/2  " \
                "|  Potencia -> x**2  |  raiz(x)  |  Infinito -> oo          " \
                "TRIGONOMETRICO:  sin(x)  |  cos(x)  |  tan(x)"
panel_ayuda = ctk.CTkLabel(vp, text=texto_ayuda, font=("Consolas", 11),
                            text_color="#003399", fg_color="#dce8ff",
                            corner_radius=8, anchor="w", padx=14, pady=7)
panel_ayuda.grid(row=2, column=0, padx=20, pady=(0, 2), sticky="ew")

# frame blanco donde se dibuja la grafica
marco_grafico = ctk.CTkFrame(vp, fg_color="white")
marco_grafico.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

#=================
#====FUNCIONES====
#=================

# crea la figura de matplotlib y la mete dentro del frame de la interfaz
def crear_grafico(contenedor):
    figura, ejes = plt.subplots(figsize=(8, 5))
    figura.patch.set_facecolor("#FFFFFF")
    ejes.set_facecolor("#ffffff")
    ejes.tick_params(colors="black")
    for borde in ejes.spines.values():
        borde.set_edgecolor("#000000")

    # limites iniciales de la pantalla
    ejes.set_xlim(0, 10)
    ejes.set_ylim(0, 10)

    ejes.axhline(0, color='black', linewidth=0.8)
    ejes.axvline(0, color='black', linewidth=0.8)
    ejes.grid(True, linestyle='--', alpha=0.5, color='gray')

    lienzo = FigureCanvasTkAgg(figura, master=contenedor)
    lienzo.get_tk_widget().pack(fill="both", expand=True)
    return figura, ejes, lienzo

#=====================================
#====FUNCION LOGICA CALCULO LIMITE====
#=====================================

def ejecutar_analsis():
    global ejes_grafico, lienzo_grafico

    texto_usuario = campo_funcion.get().strip()
    # reemplazamos raiz por sqrt que es lo que entiende sympy, y ^ por **
    texto_funcion = texto_usuario.replace('raiz', 'sqrt').replace('^', '**')
    texto_limite = campo_limite.get().strip()

    # si algun campo esta vacio no hacemos nada
    if not texto_funcion or not texto_limite:
        return

    ejes_grafico.clear()
    ejes_grafico.set_facecolor("#ffffff")

    try:
        x = sp.Symbol("x")
        funcion_simbolo = sp.sympify(texto_funcion)

        # variable para aproximarse por los costados
        aprox = 0.0001
        es_infinito = texto_limite.lower() in ["oo", "inf", "infinito"]

        if es_infinito:
            # evaluamos en numeros muy grandes para simular que x se va al infinito
            val_grande  = float(funcion_simbolo.subs(x, 1e6).evalf())
            val_grande2 = float(funcion_simbolo.subs(x, 1e7).evalf())

            # si los dos valores son casi iguales significa que converge (asintota horizontal)
            if abs(val_grande2 - val_grande) < 0.01:
                resultado = (val_grande + val_grande2) / 2
            else:
                resultado = None  # si no converge, el limite no existe

        else:
            centro = float(sp.sympify(texto_limite))

            # aproximacion manual: evaluamos muy cerca por izquierda y derecha
            valor_izquierdo = float(funcion_simbolo.subs(x, centro - aprox).evalf())
            valor_derecho = float(funcion_simbolo.subs(x, centro + aprox).evalf())

            # si ambos lados dan casi lo mismo, el limite existe
            if abs(valor_derecho - valor_izquierdo) < 0.1:
                resultado = (valor_derecho + valor_izquierdo) / 2
            else:
                resultado = None  # si ambos lados son distintos, el limite no existe

        # mostramos el resultado en pantalla
        if resultado is not None:
            texto_final = f"Resultado: {resultado:.2f}"
            etiqueta_resultado.configure(text=texto_final, text_color="#000000")
        else:
            texto_final = "Resultado: No existe el límite. \n Indefinido."
            etiqueta_resultado.configure(text=texto_final, text_color="#000000")

        # definimos el rango de x para graficar
        if es_infinito:
            inicio = 0.0
            ancho_total = 100.0
        else:
            ancho_total = 10.0
            inicio = centro - (ancho_total / 2)

        paso = ancho_total / 300

        # generamos la lista de valores en x
        lista_x = []
        for i in range(301):
            lista_x.append(inicio + (i * paso))

        # calculamos f(x) para cada punto, si falla guardamos None
        lista_y = []
        for d in lista_x:
            try:
                valor = funcion_simbolo.subs(x, d).evalf()
                if valor.is_real:
                    lista_y.append(float(valor))
                else:
                    lista_y.append(None)
            except:
                lista_y.append(None)

        ejes_grafico.plot(lista_x, lista_y, 
                          color="#0066FF", linewidth=2, 
                          label="f(x)")

        # ajustamos el zoom y dibujamos el punto rojo del limite
        if resultado is not None:
            if not es_infinito:
                ejes_grafico.plot(centro, resultado, "ro", 
                                  markersize=10, label="Límite", zorder=5)
                ejes_grafico.set_xlim(centro - 4, centro + 4)
                ejes_grafico.set_ylim(resultado - 5, resultado + 5)
                # isinstance revisa si resultado es un numero o texto
                # si es numero significa que converge, centramos el zoom ahi
                if not isinstance(resultado, str):
                    ejes_grafico.set_ylim(resultado - 5, resultado + 5)
                else:
                    # si diverge no hay numero fijo, ajustamos segun los puntos graficados
                    valores_reales = [y for y in lista_y if y is not None]
                    if valores_reales:
                            ejes_grafico.set_ylim(min(valores_reales[:150]), max(valores_reales[:150]))
        
        # ejes, cuadricula y leyenda del grafico
        ejes_grafico.axhline(0, color='black', linewidth=0.8)
        ejes_grafico.axvline(0, color='black', linewidth=0.8)
        ejes_grafico.grid(True, linestyle='--', alpha=0.5, color='gray')
        ejes_grafico.legend(facecolor="#FFFFFF", labelcolor='black')

        lienzo_grafico.draw()

    except Exception as e:
        # si hay algun error de sintaxis lo mostramos
        etiqueta_resultado.configure(text="Error de sintaxis", text_color="red")
        lienzo_grafico.draw()

boton_calcular.configure(command=ejecutar_analsis)
figura_grafico, ejes_grafico, lienzo_grafico = crear_grafico(marco_grafico)

# ejecucion de la ventana.
if __name__ == "__main__":
    vp.mainloop()