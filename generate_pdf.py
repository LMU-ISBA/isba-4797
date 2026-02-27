#!/usr/bin/env python3
"""Generate a print-ready PDF from the ISBA 4797 syllabus HTML."""

from playwright.sync_api import sync_playwright

OUTPUT_PDF = "isba-4797-syllabus.pdf"
URL = "http://localhost:8765/index.html"


def generate_pdf():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")

        # Step 1 & 2: Strip styles, remove web-only elements, restructure DOM
        page.evaluate("""() => {
            // Remove all <style> and stylesheet links
            document.querySelectorAll('style, link[rel="stylesheet"]').forEach(el => el.remove());

            // Remove hero section, nav, skip links, footer, scripts
            document.querySelectorAll(
                '.hero, nav, .mobile-nav-toggle, a[href="#course-description"], footer, script'
            ).forEach(el => el.remove());

            // Remove <br> tags ONLY outside of tables (keep them in table cells for bullet formatting)
            document.querySelectorAll('br').forEach(el => {
                if (!el.closest('table')) el.remove();
            });

            // Remove all inline style attributes
            document.querySelectorAll('[style]').forEach(el => el.removeAttribute('style'));

            // Remove table captions (screen-reader only)
            document.querySelectorAll('caption').forEach(el => el.remove());

            // Remove empty spacer rows in rubric table and fix rowspans
            document.querySelectorAll('.rubric-table tr').forEach(tr => {
                const cells = tr.querySelectorAll('td');
                if (cells.length === 1 && cells[0].textContent.trim() === '') {
                    tr.remove();
                }
            });
            // Fix rowspans after removing spacer rows (was 4, now 3)
            document.querySelectorAll('.rubric-table td[rowspan="4"]').forEach(td => {
                td.setAttribute('rowspan', '3');
            });

            // Add colgroup to rubric table for proper column widths
            const rubricTable = document.querySelector('.rubric-table table');
            if (rubricTable) {
                const colgroup = document.createElement('colgroup');
                colgroup.innerHTML = '<col style="width:50px"><col style="width:115px"><col>';
                rubricTable.insertBefore(colgroup, rubricTable.firstChild);
            }

            // Replace contact-grid divs with a simple HTML table
            const contactGrid = document.querySelector('.contact-grid');
            if (contactGrid) {
                const items = contactGrid.querySelectorAll('.contact-item');
                let tableHTML = '<table class="contact-table">';
                items.forEach(item => {
                    const label = item.querySelector('.label')?.textContent || '';
                    const valueEl = item.querySelector('.value');
                    const value = valueEl ? valueEl.innerHTML : '';
                    tableHTML += '<tr><td class="contact-label"><strong>' + label +
                                 '</strong></td><td class="contact-value">' + value + '</td></tr>';
                });
                tableHTML += '</table>';
                contactGrid.outerHTML = tableHTML;
            }

            // Inject complete print stylesheet
            const style = document.createElement('style');
            style.textContent = `
                /* Base */
                *, *::before, *::after { box-sizing: border-box; }

                html, body {
                    font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
                    font-size: 10pt;
                    line-height: 1.45;
                    color: #1a1a1a;
                    margin: 0;
                    padding: 0;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }

                body { padding: 0 8px; }

                /* Header banner */
                .header {
                    background: #1a237e !important;
                    color: white !important;
                    padding: 18px 24px;
                    margin: 0 -8px;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }
                .header-content { text-align: center; }
                .course-code {
                    font-size: 22pt; font-weight: 700; margin: 0;
                    color: white !important; letter-spacing: 1px;
                }
                .course-title {
                    font-size: 14pt; font-weight: 400; margin: 2px 0 8px 0;
                    color: rgba(255,255,255,0.9) !important;
                }
                .course-meta { font-size: 9pt; color: rgba(255,255,255,0.8) !important; }
                .course-meta .separator { margin: 0 6px; }

                /* Containers */
                .container { max-width: 100%; padding: 0; margin: 0; }
                .main-content { padding: 0; margin: 0; }
                .content-section { margin: 0; padding: 0; }

                /* Headings - CRITICAL: prevent orphaned headers */
                h2 {
                    font-size: 13pt; font-weight: 700; color: #1a237e;
                    border-bottom: 2px solid #1a237e; padding-bottom: 3px;
                    margin: 14px 0 8px 0;
                    break-after: avoid !important;
                    page-break-after: avoid !important;
                }
                h3 {
                    font-size: 10.5pt; font-weight: 600; color: #333;
                    margin: 8px 0 4px 0;
                    break-after: avoid !important;
                    page-break-after: avoid !important;
                }

                /* Text */
                p { margin: 5px 0; orphans: 3; widows: 3; }
                ol, ul { margin: 4px 0 4px 20px; padding: 0; }
                li { margin: 2px 0; }
                a { color: #1a237e; text-decoration: none; }
                em { font-style: italic; }
                strong { font-weight: 600; }

                /* Instructor */
                .instructor-info { break-inside: avoid; }
                .instructor-info h3 { font-size: 11.5pt; margin-bottom: 3px; }
                .instructor-info .bio {
                    margin-bottom: 6px; font-style: italic; color: #444;
                }

                /* Contact table */
                .contact-table {
                    width: auto; border-collapse: collapse;
                    margin: 6px 0; font-size: 9.5pt; border: none;
                }
                .contact-table td {
                    padding: 2px 10px 2px 0; vertical-align: top;
                    border: none; border-bottom: 1px solid #eee;
                }
                .contact-label { width: 100px; color: #555; white-space: nowrap; }
                .contact-value { color: #1a1a1a; }
                .contact-value a { color: #1a237e; }

                /* Objectives */
                .objectives-list { margin: 4px 0 4px 24px; }
                .objectives-list li { margin: 3px 0; }

                /* Tables */
                table {
                    width: 100%; border-collapse: collapse;
                    margin: 6px 0; font-size: 9.5pt;
                }
                th, td {
                    padding: 4px 8px; text-align: left;
                    vertical-align: top; border: 1px solid #ccc;
                }
                thead th {
                    background: #1a237e !important; color: white !important;
                    font-weight: 600; font-size: 9.5pt;
                    -webkit-print-color-adjust: exact; print-color-adjust: exact;
                }
                tr.total td {
                    font-weight: 700; background: #f0f0f0 !important;
                    -webkit-print-color-adjust: exact; print-color-adjust: exact;
                }
                tr.holiday td {
                    background: #fff3e0 !important; font-style: italic;
                    -webkit-print-color-adjust: exact; print-color-adjust: exact;
                }

                /* Grading table */
                .grading-table { max-width: 380px; break-inside: avoid; }
                .grading-table table { max-width: 380px; }
                .grading-table td:last-child,
                .grading-table th:last-child { text-align: center; width: 90px; }

                /* Grading scale grid */
                .grading-scale { margin: 10px 0; break-inside: avoid; }
                .scale-grid {
                    display: grid !important;
                    grid-template-columns: repeat(5, 1fr) !important;
                    gap: 4px !important; margin: 4px 0;
                }
                .scale-item {
                    display: flex !important; align-items: center;
                    justify-content: space-between;
                    border: 1px solid #ddd; border-radius: 3px;
                    padding: 3px 8px; font-size: 8.5pt;
                    background: #fafafa !important;
                    -webkit-print-color-adjust: exact; print-color-adjust: exact;
                }
                .scale-item .points { color: #555; font-size: 8pt; }
                .scale-item .grade { font-weight: 700; color: #1a237e; }

                /* Rubric table */
                .rubric-table table {
                    font-size: 8.5pt;
                    table-layout: fixed;
                    width: 100%;
                }
                .rubric-table th:first-child,
                .rubric-table td:first-child {
                    width: 50px; text-align: center; font-weight: 700;
                }
                .rubric-table th:nth-child(2),
                .rubric-table td:nth-child(2) {
                    width: 115px; font-weight: 600; font-size: 8pt;
                }
                .rubric-table td:nth-child(3),
                .rubric-table td:last-child {
                    text-align: left;
                }
                .rubric-table .normal-text {
                    font-weight: 400; font-size: 8pt; line-height: 1.35;
                    display: block;
                }

                /* Schedule table */
                .schedule-table td:first-child { width: 40px; text-align: center; }
                .schedule-table td:nth-child(2) { width: 130px; }

                /* Note */
                .note { font-size: 8.5pt; color: #555; font-style: italic; margin: 6px 0; }

                /* Policy sections */
                .policy { margin: 6px 0; padding: 0; }
                .policy h3 {
                    break-after: avoid !important;
                    page-break-after: avoid !important;
                }
                .policy p, .policy ul { orphans: 3; widows: 3; }

                /* Page breaks - let content flow naturally */

                /* Prevent awkward splits */
                .schedule-table { break-inside: avoid; }
            `;
            document.head.appendChild(style);
        }""")

        # Wait for styles to apply
        page.wait_for_timeout(300)

        # Generate PDF
        page.pdf(
            path=OUTPUT_PDF,
            format="Letter",
            margin={"top": "0.5in", "bottom": "0.5in", "left": "0.65in", "right": "0.65in"},
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=(
                '<div style="font-size:7px;color:#999;width:100%;text-align:center;'
                'font-family:system-ui,sans-serif;">'
                'Page <span class="pageNumber"></span> of '
                '<span class="totalPages"></span></div>'
            ),
        )

        browser.close()
        print(f"PDF saved to {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()
