function handleEdit() {
  document.getElementById('name').disabled = false;
  try {
    document.getElementById('division').disabled = false;
    document.getElementById('category').disabled = false;
  } catch (error) {

  }
  document.getElementById('club').disabled = false;
  document.getElementById('county').disabled = false;
  document.getElementById('district').disabled = false;
  document.getElementById('save').hidden = false;
  return false;
}