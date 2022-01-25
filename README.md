1. Make a parser to get info from https://kaczmarski.pl/gielda-wierzytelnosci (ex. PL5270103824). Use SQLight to save data. Make 2 tables:  
   - source (id, tin (tax no i.e.NIP), name (of company), total_amount (of debt), address, document_type, number_id, sell_for, is_exist, start_ts, parsing_ts)  
   - tins (id, tin, updated_at)

2. Logic
   * Get tin from table tins order by updated_at desc
   * Get tin from command line in terminal
     - Search info, check if exist
     - Update column updated_at in tins
     - Parse info and save 

1. Make a parser to get info from https://kaczmarski.pl/gielda-wierzytelnosci (ex. PL5270103824).  Use SQLight to save data. Make a table called `Source` with following columns:  
   - id 
   - tin (tax no i.e.NIP)
   - name (of company)
   - total_amount (of debt)
   - address
   - document_type
   - number_id
   - sell_for
   - is_exist
   - start_ts
   - parsing_ts
   - created_at
   - updated_at


