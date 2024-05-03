# Full text policy dataset

You can download the full text extracted from our law and policy dataset [HERE](https://drive.google.com/file/d/11HYmQhqfFEoj2DRRT3s4q0spw4_PPxSe/view?usp=sharing).

The dataset is in parquet files which can be loaded using pandas or whatever tools you're familiar with. We recommend loading all of the dataset into one dataframe and then filtering to start with.

If you would like to deploy your tool using this dataset after the hackathon, we will be very happy to support that! Come chat to us :)

Some key columns in the data:

\- **document_id**: the ID of the document. Note you should group by both document_id and translated to get nonduplicated text. Both translated and nontranslated documents are stored with the same document ID, so if you just group by document_id then for documents which were originally written in a language other than English, you'll get both the original language text and English text  
\- **document_metadata.name**/**document_metadata.description**: the document name and description as  in our app  
\- **document_metadata.slug**: if you append this to https://app.climatepolicyradar.org/documents/, you'll get a working link to our document viewer for that document  
\- **document_metadata.date**: the publication date of the document. Defaults to 1st January where we don't know the date; 1st of the month where we know the month but not the date  
\- **text**, **type**, **text_block_id**: these are fields related to text blocks. You can reconstruct the text of a document by sorting by text block ID. type is the block type of the document according to Azure's document parser.
