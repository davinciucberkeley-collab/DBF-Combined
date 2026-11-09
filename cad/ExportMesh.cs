// Exports every part in cad/model as a binary STL (metres, part frame, not translated) plus its display colour,
// for the interactive CAD viewer in the review page. Usage: ExportMesh.exe <cad/model dir> <out dir>
using System;
using System.IO;
using System.Collections.Generic;
using System.Globalization;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

class ExportMesh
{
    static int Main(string[] a)
    {
        string src = Path.GetFullPath(a[0]), outDir = Path.GetFullPath(a[1]); Directory.CreateDirectory(outDir);
        SldWorks sw = (SldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));
        sw.SetUserPreferenceToggle((int)swUserPreferenceToggle_e.swSTLBinaryFormat, true);
        sw.SetUserPreferenceToggle((int)swUserPreferenceToggle_e.swSTLDontTranslateToPositive, true);
        sw.SetUserPreferenceIntegerValue((int)swUserPreferenceIntegerValue_e.swExportStlUnits, (int)swLengthUnit_e.swMETER);
        sw.SetUserPreferenceIntegerValue((int)swUserPreferenceIntegerValue_e.swSTLQuality, (int)swSTLQuality_e.swSTLQuality_Custom);
        sw.SetUserPreferenceDoubleValue((int)swUserPreferenceDoubleValue_e.swSTLDeviation, 0.0004);
        sw.SetUserPreferenceDoubleValue((int)swUserPreferenceDoubleValue_e.swSTLAngleTolerance, 12 * Math.PI / 180);
        var ic = CultureInfo.InvariantCulture; var colors = new List<string>();
        foreach (string p in Directory.GetFiles(src, "*.SLDPRT"))
        {
            if (Path.GetFileName(p).StartsWith("~$")) continue;   // SOLIDWORKS lock files
            int e = 0, w = 0; string name = Path.GetFileNameWithoutExtension(p);
            ModelDoc2 d = sw.OpenDoc6(p, (int)swDocumentTypes_e.swDocPART, (int)swOpenDocOptions_e.swOpenDocOptions_Silent, "", ref e, ref w);
            if (d == null) { Console.WriteLine("open failed " + name); continue; }
            double[] m = (double[])d.MaterialPropertyValues;
            string desc, res; bool wasRes; d.Extension.get_CustomPropertyManager("").Get5("Description", false, out desc, out res, out wasRes);
            desc = (res ?? desc ?? "").Replace("\\", "/").Replace("\"", "'");
            colors.Add(string.Format(ic, "\"{0}\":{{\"c\":[{1:0.###},{2:0.###},{3:0.###}],\"d\":\"{4}\"}}", name, m[0], m[1], m[2], desc));
            string o = Path.Combine(outDir, name + ".stl");
            bool ok = d.Extension.SaveAs(o, (int)swSaveAsVersion_e.swSaveAsCurrentVersion, (int)swSaveAsOptions_e.swSaveAsOptions_Silent, null, ref e, ref w);
            Console.WriteLine((ok ? "stl " : "FAILED ") + name + (ok ? " " + new FileInfo(o).Length + " B" : ""));
            sw.CloseDoc(d.GetTitle());
        }
        File.WriteAllText(Path.Combine(outDir, "meta.json"), "{" + string.Join(",", colors) + "}\n");
        return 0;
    }
}
