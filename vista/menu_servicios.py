from datetime import datetime
from controlador.dto_indicador import IndicadorDTO
from servicios.http_seguro import ErrorServicio
from servicios.api_indicadores import INDICADORES
from servicios import api_clima
from vista import menus
from vista.entrada import pedir
from vista.validaciones import validaFecha, validaOpc, validaInt, validaConfirmacion

# Menú de indicadores: opción -> códigos que se consultan
OPCIONES_INDICADOR = [("Dólar", ["dolar"]), ("UF", ["uf"]), ("Euro", ["euro"]), ("UTM", ["utm"]),
                      ("Todos (Dólar, UF, Euro y UTM)", list(INDICADORES))]
MAX_FILAS_PANTALLA = 15


def _formato(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Pide una fecha DD-MM-AAAA (no futura) o ENTER para "último valor disponible"
def _fechaOpcional(txt: str):
    while True:
        valor = pedir(f"{txt} (DD-MM-AAAA, ENTER = último valor disponible): ").strip()
        if valor == "":
            return None
        try:
            fecha = datetime.strptime(valor, "%d-%m-%Y").date()
        except ValueError:
            print("Fecha inválida, use el formato DD-MM-AAAA (ej: 15-03-2026).")
            continue
        if fecha > datetime.now().date():
            print("La fecha no puede ser posterior a hoy.")
            continue
        return fecha


def _elegirIndicador() -> list:
    print("\nIndicador:")
    for i, (nombre, _) in enumerate(OPCIONES_INDICADOR, start=1):
        print(f"{i}. {nombre}")
    return OPCIONES_INDICADOR[validaOpc(len(OPCIONES_INDICADOR)) - 1][1]


# Muestra todos los valores si son pocos; si son muchos, un resumen + primeros y últimos
def _mostrar(lista: list) -> None:
    if len(lista) <= MAX_FILAS_PANTALLA:
        menus.listar(lista, "")
        return
    for ind in lista[:5]:
        print(ind)
    print(f"   ... ({len(lista) - 10} valores más) ...")
    for ind in lista[-5:]:
        print(ind)
    valores = [i.getValor() for i in lista]
    print(f"Resumen: {len(lista)} valores | mínimo {_formato(min(valores))} | máximo {_formato(max(valores))} "
          f"| promedio {_formato(sum(valores) / len(valores))}")


def consultarIndicadores(usuario) -> None:
    menus.titulo("Consultar Indicadores Económicos.")
    codigos = _elegirIndicador()
    print("\n1. Fecha\n2. Rango de fechas")
    modo = validaOpc(2)
    fecha = desde = hasta = None
    if modo == 1:
        fecha = _fechaOpcional("Fecha a consultar")
    else:
        desde = validaFecha("Fecha inicial", permitirFutura=False)
        hasta = validaFecha("Fecha final", permitirFutura=False)
    dto = IndicadorDTO()
    for codigo in codigos:
        print(f"\n--- {INDICADORES[codigo]} ---")
        try:
            lista = dto.consultar(usuario, codigo, fecha, desde, hasta)
        except ErrorServicio as ex:
            print(f"-{ex}-")
            continue
        if not lista:
            print("No hay valores publicados para esa fecha o rango (fin de semana, feriado o fecha sin datos).")
            continue
        if codigo == "utm" and fecha is not None and lista[0].getFecha() != fecha:
            print("(La UTM es un valor mensual: se muestra el valor del mes.)")
        _mostrar(lista)
        print(dto.guardar(lista))


def verHistorial(usuario) -> None:
    menus.titulo("Indicadores almacenados en la Base de Datos.")
    codigos = _elegirIndicador()
    dto = IndicadorDTO()
    for codigo in codigos:
        print(f"\n--- {INDICADORES[codigo]} (últimos 30 almacenados) ---")
        try:
            lista = dto.historial(usuario, codigo)
        except ErrorServicio as ex:
            return print(f"-{ex}-")
        if lista is None:
            print("-No se pudo leer el historial.-")
        else:
            menus.listar(lista, "No hay valores almacenados.")


# Convierte el sueldo de un empleado a moneda extranjera con el valor más reciente (pagos internacionales)
def convertirSalario(usuario) -> None:
    menus.titulo("Calcular Sueldo en Moneda Extranjera.")
    emp = menus.seleccionarEmpleado()
    if emp is None:
        return
    print("\nMoneda: 1. Dólar | 2. Euro")
    codigo = "dolar" if validaOpc(2) == 1 else "euro"
    try:
        lista = IndicadorDTO().consultar(usuario, codigo)
    except ErrorServicio as ex:
        return print(f"-{ex}-")
    if not lista:
        return print("No hay un valor disponible para convertir.")
    if not isinstance(emp.getSalario(), int):
        return print("-No se pudo leer el sueldo del empleado (dato ilegible).-")
    ind = lista[0]
    print(f"{INDICADORES[codigo]} al {ind.getFecha().strftime('%d-%m-%Y')}: ${_formato(ind.getValor())} (fuente: {ind.getAutor()})")
    print(f"Sueldo de {emp.getNombre()} {emp.getApellido()}: ${_formato(emp.getSalario())} CLP "
          f"= {_formato(emp.getSalario() / ind.getValor())} {'USD' if codigo == 'dolar' else 'EUR'}")
    if validaConfirmacion("¿Desea guardar este valor del indicador en la base de datos?"):
        print(IndicadorDTO().guardar(lista))


def consultarClima(usuario) -> None:
    menus.titulo("Clima y Energía Solar (apoyo a proyectos solares y ambientales).")
    while True:
        ciudad = pedir("Ciudad (solo letras): ").strip()
        if api_clima.validarCiudad(ciudad):
            break
        print("Ciudad inválida: use solo letras (2 a 60 caracteres).")
    while True:
        pais = pedir("País (código de 2 letras, ej: CL, AR, PE; ENTER para omitir): ").strip()
        if pais == "" or api_clima.validarPais(pais):
            break
        print("Código de país inválido: use 2 letras (ej: CL).")
    try:
        c, recomendacion = IndicadorDTO().clima(usuario, ciudad, pais)
    except ErrorServicio as ex:
        return print(f"-{ex}-")
    lugar = c["lugar"]
    region = f", {lugar['region']}" if lugar["region"] else ""
    print(f"\nCondiciones actuales en {lugar['nombre']}{region} ({lugar['pais']})")
    print(f"Estado: {c['estado']} | Temperatura: {c['temperatura']:.1f} °C | Humedad: {c['humedad']:.0f} %")
    print(f"Nubosidad: {c['nubosidad']:.0f} % | Radiación solar ahora: {c['radiacion']:.0f} W/m² | "
          f"Viento: {c['viento']:.0f} km/h | Precipitación: {c['precipitacion']:.1f} mm")
    print("\nPronóstico (energía solar disponible y condiciones de trabajo):")
    for d in c["pronostico"]:
        lluvia = f"{d['lluvia']}%" if isinstance(d["lluvia"], (int, float)) else "-"
        print(f"  {d['fecha']}: {d['estado']}, {d['minima']:.0f}° a {d['maxima']:.0f}° C | "
              f"Sol {d['sol']:.1f} h | Energía {d['energia']:.1f} kWh/m² | UV {d['uv']:.0f} | "
              f"Ráfagas {d['rafagas']:.0f} km/h | Lluvia {lluvia}")
    print("\nEvaluación para proyectos solares y ambientales:")
    for linea in recomendacion:
        print(f"  - {linea}")


def menuServicios(usuario) -> None:
    menus.ejecutarMenu("Servicios Externos (APIs)", [
        ("Consultar indicadores económicos (Dólar, UF, Euro, UTM)", lambda: consultarIndicadores(usuario)),
        ("Ver indicadores almacenados", lambda: verHistorial(usuario)),
        ("Calcular sueldo en moneda extranjera", lambda: convertirSalario(usuario)),
        ("Clima y energía solar de una ciudad", lambda: consultarClima(usuario))])
