import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Eye, X } from "lucide-react";

interface ExportPreviewProps {
  htmlContent: string;
  title: string;
}

export const ExportPreview = ({ htmlContent, title }: ExportPreviewProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Eye className="w-4 h-4 mr-2" />
          Visualizar
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-6xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Prévia do {title}</span>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setIsOpen(false)}
              className="h-6 w-6 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>
        <div className="border rounded-lg overflow-hidden bg-white">
          <iframe
            srcDoc={htmlContent}
            className="w-full h-[60vh]"
            title="Export Preview"
            sandbox="allow-same-origin"
          />
        </div>
        <div className="flex justify-end gap-2 pt-4">
          <Button 
            variant="outline" 
            onClick={() => setIsOpen(false)}
          >
            Fechar
          </Button>
          <Button 
            onClick={() => {
              const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `sipal_preview_${new Date().toISOString().split('T')[0]}.html`;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              URL.revokeObjectURL(url);
            }}
            className="bg-sipal-blue hover:bg-sipal-blue-light"
          >
            Baixar HTML
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};