CREATE PROCEDURE refresh_data AS
BEGIN
  INSERT INTO app.target_table SELECT * FROM app.source_table;
  -- DELETE FROM ignored_table;
  EXECUTE IMMEDIATE dynamic_statement;
END;
