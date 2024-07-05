import { type IWebpageProps } from "./Webpage.types";

const Webpage = ({ page, project }: IWebpageProps): JSX.Element => {
  return (
    <>
      <div>
        <label htmlFor="page-link">Link to page:&nbsp;</label>
        <a href={`https://${project}${page.name}`} id="page-link" rel="noopener noreferrer" target="_blank">
          {`https://${project}${page.name}`}
        </a>
      </div>
      <div>
        <label htmlFor="page-title">Title:</label>
        <input id="page-title" readOnly type="text" value={page.title || "-"} />
      </div>
      <div>
        <label htmlFor="page-descr">Description:</label>
        <textarea id="page-descr" readOnly value={page.description || "-"} />
      </div>
      <div>
        <label htmlFor="page-copy-doc">Copy doc:&nbsp;</label>
        {page.link ? (
          <a href={page.link} id="page-link" rel="noopener noreferrer" target="_blank">
            {page.link}
          </a>
        ) : (
          <input defaultValue={page.link || "-"} id="page-copy-doc" type="text" />
        )}
      </div>
    </>
  );
};

export default Webpage;
