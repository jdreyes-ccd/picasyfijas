# Picas y Fijas - Juego de Adivinanza

Un juego interactivo donde los jugadores intentan adivinar un número secreto de 4 cifras con dígitos diferentes. El juego soporta tanto modo individual como multijugador.

## Integrantes:
- Juan Diego Reyes Martinez - Codigo: 161004329
- Diego Andres Chavez - Código: 1006820738

## Historias de Usuario y Criterios de Aceptación

### Modo Individual

#### **Historia de Usuario 1: Jugar Solo**
**Como** jugador individual  
**Quiero** jugar contra la computadora  
**Para** practicar y divertirme sin necesidad de otro jugador

**Criterios de Aceptación:**
- El jugador debe poder iniciar un juego individual sin necesidad de registrarse
- El sistema debe generar un número aleatorio de 4 dígitos diferentes
- El jugador tiene máximo 10 intentos para adivinar el número
- Después de cada intento, el sistema muestra:
  - Número de picas (dígitos correctos en posición incorrecta)
  - Número de fijas (dígitos correctos en posición correcta)
- El juego termina cuando:
  - El jugador adivina el número (gana)
  - Se agotan los 10 intentos (pierde)
- El sistema debe mostrar el número secreto al finalizar el juego

---

### Modo Multijugador

#### **Historia de Usuario 2: Jugar Contra Otro Usuario**
**Como** jugador  
**Quiero** jugar contra otra persona  
**Para** competir y divertirme con amigos

**Criterios de Aceptación:**
- Los jugadores deben poder identificarse con un nombre (sin autenticación)
- Un jugador debe poder crear una sala de juego
- Otro jugador debe poder unirse a la sala existente
- Cada jugador debe poder establecer su número secreto de 4 dígitos diferentes
- Los jugadores se turnan para hacer intentos
- Después de cada intento, el sistema muestra las picas y fijas correspondientes
- El juego termina cuando un jugador adivina el número del oponente
- El sistema debe declarar un ganador claramente

---

### Funcionalidades Comunes

#### **Historia de Usuario 3: Validación de Números**
**Como** jugador  
**Quiero** que el sistema valide mis intentos  
**Para** asegurarme de que estoy jugando correctamente

**Criterios de Aceptación:**
- El sistema debe rechazar números que no tengan exactamente 4 dígitos
- El sistema debe rechazar números con dígitos repetidos
- El sistema debe mostrar mensajes de error claros cuando la validación falla
- El sistema no debe contar como intento los números inválidos

#### **Historia de Usuario 4: Interfaz de Usuario Intuitiva**
**Como** jugador  
**Quiero** una interfaz fácil de usar  
**Para** poder jugar sin confusiones

**Criterios de Aceptación:**
- La interfaz debe mostrar claramente el estado actual del juego
- Debe ser evidente de quién es el turno en modo multijugador
- Los intentos anteriores deben ser visibles para referencia
- Las instrucciones del juego deben ser accesibles




