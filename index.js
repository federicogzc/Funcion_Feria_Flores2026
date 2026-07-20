const VoximplantKit = require('@voximplant/kit-functions-sdk').default;
const axios = require('axios');

module.exports = async function (context, callback) {
  const kit = new VoximplantKit(context);

  // 1) Leer variables del flujo
  const dia    = kit.getVariable('dia');
  const mes    = kit.getVariable('mes');
  const anio   = kit.getVariable('anio');
  const cedula = kit.getVariable('cedula');
  const numero = kit.getVariable('numero');

  // 2) Endpoint SheetDB desde variable de entorno, con fallback
  const sheetdbURL =
    kit.getEnvVariable('SHEETDB_URL') ||
    'https://sheetdb.io/api/v1/yd1nip9qjq315';

  try {
    if (!numero) {
      throw new Error('La variable "numero" no está definida.');
    }

    // 3) ¿Ya existe el número?
    const { data: registros } = await axios.get(`${sheetdbURL}/search`, {
      params: { numero },          // ?numero=XXXXXXXX
      timeout: 6000,
    });                                                   //:contentReference[oaicite:2]{index=2}

    if (Array.isArray(registros) && registros.length > 0) {
      kit.setVariable('responseMessage', 'Número ya registrado.');
    } else {
      // 4) Construir fila limpiando campos vacíos
      const fila = { dia, mes, anio, cedula, numero };
      Object.keys(fila).forEach(k => {
        if (!fila[k]) delete fila[k];
      });

      if (Object.keys(fila).length === 0) {
        throw new Error('No se recibió ningún dato válido para guardar.');
      }

      // 5) Insertar (SheetDB => data: [ { … } ])
      await axios.post(sheetdbURL, { data: [fila] }, { timeout: 6000 });  //:contentReference[oaicite:3]{index=3}
      kit.setVariable('responseMessage', 'Información guardada exitosamente.');
    }
  } catch (err) {
    console.error('[Function sheetdbRegister]', err);
    kit.setVariable('responseMessage', 'Ocurrió un error, por favor intente de nuevo más tarde.');
    kit.setVariable('error', err.message);
  }

  // 6) Responder al bloque Function request
  callback(200, kit.getResponseBody());
};
