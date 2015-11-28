#include <stdio.h>
#include <string.h>
#include <ctype.h>

char titulo[100];
char label[100];
char classes[20][100];
double precisions[20];
double recalls[20];
double f1s[20];
int confusion[20][20];
double acuracia, kappa, acuraciaEsperada;
const int MAX_CLASS = 11;

int t=0;
void tabs(){
	for(int i=0;i<t;i++)printf("\t");
}

int main(){
	printf("Para este exemplo tem-se:\n\n");
	gets(titulo);
	strcpy(label, "tab:");
	int maxlabel=strlen(label);
	for(int i=0;titulo[i];i++){
		label[maxlabel++] = titulo[i]==' '?'_':tolower(titulo[i]);
	}
	for(int i=0;i<MAX_CLASS;i++) {
		gets(classes[i]);
	}
	
	for(int i=0;i<MAX_CLASS;i++) {
		scanf("%lf %lf %lf", &precisions[i], &recalls[i], &f1s[i]);
	}

	for(int i=0;i<MAX_CLASS;i++) {
		for(int j=0;j<MAX_CLASS;j++) {
			scanf("%d", &confusion[i][j]);
		}
	}

	scanf("%lf / %lf",&kappa, &acuracia);
	acuraciaEsperada = (acuracia-kappa)/(1-kappa);

	printf("$acuracia=%lf$\n\n", acuracia);
	printf("$acuracia\\_esperada=%lf$\n\n", acuraciaEsperada);
	printf("$Kappa=%lf$\n", kappa);
	printf("\n\n");

	printf("A Tabela \\ref{%s} apresenta a matriz de confusao.\n\n\n", label);

	printf("\\begin{table}[tph]\n");
	t++;
	tabs();
	printf("\\begin{center}\n");
	t++;
	tabs();
	printf("\\begin{tabular}{");
	for(int i=0;i<MAX_CLASS;i++)printf(" c ");
	printf("}\n");
	t++;
	tabs();
	printf("\\hline\n");
	tabs();
	//printf("Classificado \\\\ Real");
	for(int i=0;i<MAX_CLASS;i++){
		if(i!=0)printf(" & ");
		for(int j=0;j<3;j++)printf("%c", classes[i][j]);
	}
	printf("\\\\\n");
	tabs();
	printf("\\hline\n");
	for(int i=0;i<MAX_CLASS;i++){
		tabs();	
		//printf("%s", classes[i]);
		for(int j=0;j<MAX_CLASS;j++){
			if(j!=0)printf(" & ");
			printf("%d", confusion[i][j]);
		}
		printf("\\\\\n");
	}
	tabs();
	printf("\\hline\n");
	t--;
	tabs();
	printf("\\end{tabular}\n");
	t--;
	tabs();
	printf("\\end{center}\n");
	tabs();
	printf("\\caption{Matriz de confusao para a %s}\n", titulo);
	tabs();
	printf("\\label{%s}\n", label);
	t--;
	tabs();
	printf("\\end{table}\n");

	printf("\n\n");

	printf("A Figura \\ref{fig:%s} consiste numa representação gráfica da matriz de confusão.\n\n",label+4);

	printf("\\begin{figure}[ht!]\n");
	t++;
	tabs();
	printf("\\centering"); 
	tabs();
	printf("\\includegraphics[width=0.9\\textwidth]{%s.png}\n", label+4);
	tabs();
	printf("\\caption{Heatmap da matriz de confusão da Tabela \\ref{%s}}\n",label);
	tabs();
	printf("\\label{fig:%s}\n", label+4);
	t--;
	tabs();
	printf("\\end{figure}\n");
	tabs();
	printf("\nOutras estatísticas analisadas são as precisões, as abrangências e os f1scores para cada uma das classes, conforme relacionado na Tabela \\ref{%s_prec_rec}.\n\n", label);

	printf("\\begin{table}[tph]\n");
	t++;
	tabs();
	printf("\\begin{center}\n");
	t++;
	tabs();
	printf("\\begin{tabular}{");
	for(int i=0;i<4;i++)printf(" c ");
	printf("}\n");
	t++;
	tabs();
	printf("\\hline\n");
	tabs();
	printf("Classe & Precisao & Abrangencia & F1score \\\\\n");
	tabs();
	printf("\\hline\n");
	for(int i=0;i<MAX_CLASS;i++){
		tabs();	
		for(int j=0;classes[i][j] && classes[i][j]!=' ';j++)printf("%c", classes[i][j]);
		printf(" & %lf & %lf & %lf ", precisions[i], recalls[i], f1s[i]);
		printf("\\\\\n");
	}
	double mediaPrecision=0, mediaRecall=0;
	for (int i=0;i<MAX_CLASS;i++){
		mediaPrecision+=precisions[i];
		mediaRecall+=recalls[i];
	}
	mediaPrecision/=MAX_CLASS;
	mediaRecall/=MAX_CLASS;

	tabs();
	printf("Media Micro & %lf & %lf & %lf \\\\\n", acuracia, acuracia, acuracia);
	tabs();
	printf("Media Macro & %lf & %lf & %lf \\\\\n", mediaPrecision, mediaRecall, mediaPrecision*mediaRecall*2/(mediaPrecision+mediaRecall));
	tabs();
	printf("\\hline\n");
	t--;
	tabs();
	printf("\\end{tabular}\n");
	t--;
	tabs();
	printf("\\end{center}\n");
	tabs();
	printf("\\caption{Precisão e abrangencia para %s}\n", titulo);
	tabs();
	printf("\\label{%s_prec_rec}\n", label);
	t--;
	tabs();
	printf("\\end{table}\n");

	printf("\n\n");

	for(int i=0;i<MAX_CLASS;i++) {
		for(int j=0;j<MAX_CLASS;j++) {
			printf("%5d", confusion[MAX_CLASS - i - 1][j]);
		}
		printf("\n");
	}
}